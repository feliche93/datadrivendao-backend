{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
),

twitter_users_scd AS (
    SELECT * 
    FROM {{ source('raw_data', 'twitter_users_scd') }}
),

transformed AS (

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
    
)

SELECT 
    transformed.*,
    followers - LEAD(followers, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS followers_change,
    friends - LEAD(friends, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS friends_change,
    listed - LEAD(listed, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS listed_change,
    favourites - LEAD(favourites, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS favourites_change,
    statuses - LEAD(statuses, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS statuses_change,
FROM transformed