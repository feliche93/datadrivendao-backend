cube(`Snapshot`, {
  sql: `SELECT * FROM dbt_fvemmer.fct_snapshot`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started  
  },
  
  joins: {
    DAO: {
      relationship: 'hasOne',
      sql: `${Snapshot}.dao_id = ${DAO}.id`
    }
  },
  
  measures: {
    count: {
      type: `count`,
      drillMembers: [daoId]
    },

    followers: {
      sql: `followers`,
      type: `sum`
    },
    
    proposals: {
      sql: `proposals`,
      type: `sum`
    },
    
    voters1d: {
      sql: `voters_1d`,
      type: `sum`,
      title: `Voters 1d`
    },
    
    proposals1d: {
      sql: `proposals_1d`,
      type: `sum`,
      title: `Proposals 1d`
    },
    
    followers1d: {
      sql: `followers_1d`,
      type: `sum`,
      title: `Followers 1d`
    }
  },
  
  dimensions: {
    daoId: {
      sql: `dao_id`,
      type: `string`,
      primaryKey: true
    },
  }
});
