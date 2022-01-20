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
        COALESCE(snapshot_spaces.twitter, twitter_screen_names.twitter) AS twitter,
        snapshot_spaces.github,
        snapshot_spaces.website,
        snapshot_spaces.avatar,
        snapshot_spaces.network
    FROM snapshot_explore
    LEFT JOIN snapshot_spaces ON snapshot_explore.index = snapshot_spaces.id 
    LEFT JOIN twitter_screen_names ON twitter_screen_names.id = snapshot_spaces.id
    ORDER BY followers DESC
    -- currently only focusing on 500 DAOs
    LIMIT 500

),

final AS (

   SELECT DISTINCT
        combined.id,
        combined.name, 
        symbol,
        COALESCE(twitter_users.description, about) AS about,
        twitter,
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
        github,
        website,
        avatar,
        network
    FROM combined
    LEFT JOIN twitter_users ON combined.twitter = twitter_users.screen_name

)

SELECT *
FROM final