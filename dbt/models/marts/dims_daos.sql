{{ config(materialized='table') }}

WITH snapshot_explore AS (
    SELECT * 
    FROM {{ source('raw_data', 'snapshot_explore') }}
),

snapshot_spaces AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_spaces') }}
),

twitter_screen_names AS (
    SELECT *
    FROM {{ source('raw_data', 'twitter_screen_names') }}
),

twitter_users AS (
    SELECT *
    FROM {{ source('raw_data', 'twitter_users') }}
),

combined AS (

    SELECT
        snapshot_spaces.id,
        snapshot_spaces.name, 
        snapshot_spaces.symbol,
        snapshot_spaces.about,
        snapshot_spaces.location,
        COALESCE(snapshot_spaces.twitter, twitter_screen_names.twitter) AS twitter,
        snapshot_spaces.github,
        snapshot_spaces.website,
        CASE 
            WHEN CONTAINS_SUBSTR(snapshot_spaces.avatar, 'ipfs') THEN REGEXP_REPLACE(snapshot_spaces.avatar, r'ipfs://', r'https://ipfs.io/ipfs/')
            WHEN snapshot_spaces.avatar = '' THEN NULL
            ELSE NULL
        END AS avatar,
        snapshot_spaces.network
    FROM snapshot_explore
    LEFT JOIN snapshot_spaces ON snapshot_explore.index = snapshot_spaces.id 
    LEFT JOIN twitter_screen_names ON twitter_screen_names.id = snapshot_spaces.id
    -- currently limit to more than 100 followers
    WHERE followers >= 50
    ORDER BY followers DESC
),

final AS (

   SELECT DISTINCT
        combined.id,
        combined.name, 
        combined.symbol,
        COALESCE(combined.location, twitter_users.location) AS location,
        CASE 
            WHEN combined.about = '' THEN twitter_users.description
            ELSE combined.about
        END AS about,
        combined.twitter,
        CAST(
            PARSE_TIMESTAMP(
                "%a %b %d %H:%M:%S %Y",
                CONCAT(
                    SUBSTR(twitter_users.created_at, 0, 19),
                    ' ',
                    SUBSTR(twitter_users.created_at, 27, 4)
                    )
            ) AS DATE
        ) AS twitter_created_date,
        combined.github,
        combined.website,
        --combined.avatar,
        --twitter_users.profile_image_url,
        COALESCE(REPLACE(twitter_users.profile_image_url, '_normal',''), combined.avatar) AS avatar,
        combined.network
    FROM combined
    LEFT JOIN twitter_users ON combined.twitter = twitter_users.screen_name

)

SELECT *
FROM final