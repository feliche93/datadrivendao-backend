WITH explore AS (
    SELECT * 
    FROM {{ source('raw_data', 'snapshot_explore') }}
),

spaces AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_spaces') }}
),

missing_screen_names AS (
    SELECT *
    FROM {{ source('raw_data', 'twitter_screen_names') }}
),

combined AS (

    SELECT
        spaces.id,
        spaces.name, 
        spaces.symbol,
        spaces.about,
        COALESCE(spaces.twitter, missing_screen_names.twitter) AS twitter,
        spaces.github,
        spaces.website,
        spaces.avatar,
        spaces.network
    FROM explore
    LEFT JOIN spaces ON explore.index = spaces.id 
    LEFT JOIN missing_screen_names ON missing_screen_names.id = spaces.id
    ORDER BY followers DESC
    LIMIT 500

)

SELECT *
FROM combined