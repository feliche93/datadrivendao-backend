{{ config(materialized='table') }}

WITH twitter_history AS (

    SELECT * 
    FROM {{ ref('fct_twitter_history') }}

),

average_stats AS (

    SELECT 
        screen_name,
        AVG(followers) AS avg_followers,
        AVG(friends) AS avg_friends,
        AVG(listed) AS avg_listed,
        count(*) AS samples
    FROM twitter_history
    GROUP BY 1

),

global_avg_stats AS (

    SELECT 
        AVG(avg_followers) AS global_avg_followers,
        AVG(avg_friends) AS global_avg_friends,
        AVG(avg_listed) AS global_avg_listed
    FROM average_stats

)

SELECT *
FROM average_stats
CROSS JOIN global_avg_stats