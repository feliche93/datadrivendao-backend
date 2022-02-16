{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
)

SELECT
    dao_id,
    twitter_users.created_at,
    DATE_DIFF(
        CURRENT_DATE(),
        CAST(
            PARSE_TIMESTAMP(
                "%a %b %d %H:%M:%S %Y",
                CONCAT(
                    SUBSTR(twitter_users.created_at, 0, 19),
                    ' ',
                    SUBSTR(twitter_users.created_at, 27, 4)
                )
            ) AS DATE
        ),
        DAY
    ) AS days_since_created,
    --PARSE_TIMESTAMP("%a %b %d %H:%M:%S %SSSZ %Y", twitter_users.created_at),
    --EXTRACT(DATE  FROM twitter_users.created_at),
    twitter_users.followers_count AS total_followers,
    twitter_users.friends_count AS total_friends,
    twitter_users.listed_count AS total_listed,
    twitter_users.favourites_count AS total_favourites,
    twitter_users.statuses_count AS total_statuses
FROM dim_dao
LEFT JOIN {{ source('raw_data', 'twitter_users') }} ON twitter_users.screen_name = dim_dao.twitter
WHERE created_at IS NOT NULL