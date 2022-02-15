cube(`Twitter`, {
  sql: `SELECT * FROM dbt_fvemmer.fct_twitter`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started  
  },
  
  joins: {
    DAO: {
      relationship: 'hasOne',
      sql: `${Twitter}.dao_id = ${DAO}.id`
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
    
    friends: {
      sql: `friends`,
      type: `sum`
    },
    
    listed: {
      sql: `listed`,
      type: `sum`
    },
    
    favourites: {
      sql: `favourites`,
      type: `sum`
    },
    
    statuses: {
      sql: `statuses`,
      type: `sum`
    },

    daySinceCreated: {
      sql: `days_since_created`,
      type: `sum`
    },
  },
  
  dimensions: {
    daoId: {
      sql: `dao_id`,
      type: `string`,
      primaryKey: true
    }
  }
});
