{{ config(materialized='table') }}

WITH dim_daos AS (
    SELECT *
    FROM {{ ref('dim_daos') }}
),

twitter_users_scd AS (
    SELECT * 
    FROM {{ source('raw_data', 'twitter_users_scd') }}
)

SELECT
    dim_daos.id AS dao_id,
    twitter_users_scd.created_at,
    CAST(scraped_at AS DATE) AS scraped_date,
    --PARSE_TIMESTAMP("%a %b %d %H:%M:%S %SSSZ %Y", twitter_users_scd.created_at),
    --EXTRACT(DATE  FROM twitter_users_scd.created_at),
    twitter_users_scd.followers_count AS followers,
    twitter_users_scd.friends_count AS friends,
    twitter_users_scd.listed_count AS listed,
    twitter_users_scd.favourites_count AS favourites,
    twitter_users_scd.statuses_count AS statuses
FROM twitter_users_scd
LEFT JOIN dim_daos ON twitter_users_scd.screen_name = dim_daos.twitter
WHERE created_at IS NOT NULL