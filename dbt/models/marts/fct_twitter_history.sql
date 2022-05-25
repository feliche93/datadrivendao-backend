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
        twitter_users_scd.followers_count AS total_followers,
        twitter_users_scd.friends_count AS total_friends,
        twitter_users_scd.listed_count AS total_listed,
        twitter_users_scd.favourites_count AS total_favourites,
        twitter_users_scd.statuses_count AS total_statuses
    FROM twitter_users_scd
    INNER JOIN dim_dao ON twitter_users_scd.screen_name = dim_dao.twitter
    WHERE scraped_at IS NOT NULL
    
)

SELECT 
    transformed.*,
    total_followers - LEAD(total_followers, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS followers,
    total_friends - LEAD(total_friends, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS friends,
    total_listed - LEAD(total_listed, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS listed,
    total_favourites - LEAD(total_favourites, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS favourites,
    total_statuses - LEAD(total_statuses, 1) OVER (PARTITION BY dao_id ORDER BY scraped_date DESC) AS statuses,
FROM transformed