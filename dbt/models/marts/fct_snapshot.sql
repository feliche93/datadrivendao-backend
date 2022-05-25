{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
),

snapshot_explore AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_explore') }}
),

snapshot_spaces AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_spaces') }}
)

SELECT
    dao_id,
    followers AS total_followers,
    proposals AS total_proposals,
    voters_1d AS voters,
    proposals_1d AS proposals,
    followers_1d AS followers
FROM dim_dao
LEFT JOIN snapshot_explore ON snapshot_explore.index = dim_dao.dao_id
LEFT JOIN snapshot_spaces ON snapshot_spaces.id = dim_dao.dao_id
