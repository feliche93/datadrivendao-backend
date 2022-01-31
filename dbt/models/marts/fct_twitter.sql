{{ config(materialized='table') }}

WITH dims_daos AS (
    SELECT *
    FROM {{ ref('dims_daos') }}
)

SELECT
    dims_daos.id AS dao_id,
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
    twitter_users.followers_count AS followers,
    twitter_users.friends_count AS friends,
    twitter_users.listed_count AS listed,
    twitter_users.favourites_count AS favourites,
    twitter_users.statuses_count AS statuses
FROM dims_daos
LEFT JOIN {{ source('raw_data', 'twitter_users') }} ON twitter_users.screen_name = dims_daos.twitter
WHERE created_at IS NOT NULL