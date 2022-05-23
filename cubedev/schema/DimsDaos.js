cube(`DAO`, {
  sql: `SELECT * FROM dbt_fvemmer.dim_daos`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started  
  },
  
  joins: {
    Twitter: {
      relationship: 'hasOne',
      sql: `${Twitter}.dao_id = ${DAO}.id`
    },
    TwitterHistory: {
      relationship: 'hasOne',
      sql: `${TwitterHistory}.dao_id = ${DAO}.id`
    },
    Snapshot: {
      relationship: 'hasOne',
      sql: `${Snaphot}.dao_id = ${DAO}.id`
    }
    
  },
  
  measures: {
    count: {
      type: `count`,
      drillMembers: [id, name]
    }
  },
  
  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },

    twitterCreatedDate: {
      sql: `PARSE_TIMESTAMP('%Y-%m-%d', twitter_created_date)`,
      type: `time`
    },
    
    name: {
      sql: `name`,
      type: `string`
    },
    
    symbol: {
      sql: `symbol`,
      type: `string`
    },
    
    about: {
      sql: `about`,
      type: `string`
    },

    location: {
      sql: `about`,
      type: `string`
    },
    
    twitter: {
      sql: `twitter`,
      type: `string`
    },
    
    github: {
      sql: `github`,
      type: `string`
    },
    
    website: {
      sql: `website`,
      type: `string`
    },
    
    avatar: {
      sql: `avatar`,
      type: `string`
    },
    
    network: {
      sql: `network`,
      type: `string`
    }
  }
});
