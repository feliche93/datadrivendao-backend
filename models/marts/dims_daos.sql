WITH explore AS (
    SELECT * 
    FROM {{ source('raw_data', 'snapshot_explore') }}
),

spaces AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_spaces') }}
),

combined AS (

    SELECT
        spaces.id,
        spaces.name, 
        spaces.symbol,
        spaces.about,
        spaces.twitter,
        spaces.github,
        spaces.website,
        spaces.avatar,
        spaces.network
    FROM explore
    LEFT JOIN spaces ON explore.index = spaces.id 
    ORDER BY followers DESC
    LIMIT 500

)

SELECT *
FROM combined