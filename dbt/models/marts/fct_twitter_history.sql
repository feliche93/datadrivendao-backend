{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
),

twitter_users_scd AS (
    SELECT * 
    FROM {{ source('raw_data', 'twitter_users_scd') }}
)

SELECT DISTINCT
    dao_id,
    CAST(
        PARSE_TIMESTAMP(
        "%F",
        SUBSTR(twitter_users_scd.scraped_at, 0, 10)
    ) AS DATE) AS scraped_date,
    twitter_users_scd.followers_count AS followers,
    twitter_users_scd.friends_count AS friends,
    twitter_users_scd.listed_count AS listed,
    twitter_users_scd.favourites_count AS favourites,
    twitter_users_scd.statuses_count AS statuses
FROM twitter_users_scd
INNER JOIN dim_dao ON twitter_users_scd.screen_name = dim_dao.twitter
WHERE scraped_at IS NOT NULL