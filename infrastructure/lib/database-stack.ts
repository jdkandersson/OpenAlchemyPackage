import * as cdk from '@aws-cdk/core';
import * as regionInfo from '@aws-cdk/region-info';
import * as dynamodb from '@aws-cdk/aws-dynamodb';

import { CONFIG } from './config';
import { ENVIRONMENT } from './environment';

export class DatabaseStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Shared properties
    const sub = { name: 'sub', type: dynamodb.AttributeType.STRING };

    // Database for the specs
    const tableReplicationRegions = [
      // 'ap-south-1',
      // 'eu-north-1',
      // 'eu-west-3',
      // 'eu-south-1',
      // 'eu-west-2',
      // 'eu-west-1',
      // 'ap-northeast-2',
      // 'ap-northeast-1',
      // 'ca-central-1',
      // 'sa-east-1',
      // 'ap-southeast-1',
      'ap-southeast-2',
      // 'eu-central-1',
      // 'us-east-1',
      // 'us-east-2',
      // 'us-west-1',
      // 'us-west-2',
    ].filter((region) => region != ENVIRONMENT.AWS_DEFAULT_REGION);
    const specsTable = new dynamodb.Table(this, 'SpecsTable', {
      partitionKey: { ...sub },
      tableName: CONFIG.database.spec.tableName,
      sortKey: {
        name: 'updated_at_id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      replicationRegions: tableReplicationRegions,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });
    specsTable.addLocalSecondaryIndex({
      indexName: CONFIG.database.spec.localSecondaryIndexName,
      sortKey: {
        name: 'id_updated_at',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Database for the credentials
    const credentialsTable = new dynamodb.Table(this, 'CredentialsTable', {
      partitionKey: { ...sub },
      tableName: CONFIG.database.credentials.tableName,
      sortKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      replicationRegions: tableReplicationRegions,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });
    credentialsTable.addGlobalSecondaryIndex({
      indexName: CONFIG.database.credentials.globalSecondaryIndexName,
      partitionKey: { name: 'public_key', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });
  }
}
