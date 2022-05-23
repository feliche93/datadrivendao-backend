
WITH twitter_users AS (
    SELECT * 
    FROM {{ source('twitter', 'users') }}
),

transformed AS (
    SELECT DISTINCT
        screen_name,
        CAST(scraped_at AS DATE) AS scraped_date,
        followers_count AS total_followers,
        friends_count AS total_friends,
        listed_count AS total_listed,
        favourites_count AS total_favourites,
        statuses_count AS total_statuses
    FROM twitter_users
)

SELECT 
    transformed.*,
    total_followers - LEAD(total_followers, 1) OVER (PARTITION BY screen_name ORDER BY scraped_date DESC) AS followers,
    total_friends - LEAD(total_friends, 1) OVER (PARTITION BY screen_name ORDER BY scraped_date DESC) AS friends,
    total_listed - LEAD(total_listed, 1) OVER (PARTITION BY screen_name ORDER BY scraped_date DESC) AS listed,
    total_favourites - LEAD(total_favourites, 1) OVER (PARTITION BY screen_name ORDER BY scraped_date DESC) AS favourites,
    total_statuses - LEAD(total_statuses, 1) OVER (PARTITION BY screen_name ORDER BY scraped_date DESC) AS statuses,
FROM transformed
WHERE screen_name = 'developer_dao'