#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';

import { ApiStack } from '../lib/api-stack';
import { WebStack } from '../lib/web-stack';
import { ENVIRONMENT } from '../lib/environment';

const env = {
  account: ENVIRONMENT.AWS_ACCOUNT,
  region: ENVIRONMENT.AWS_DEFAULT_REGION,
};

const app = new cdk.App();
if (ENVIRONMENT.STACK === 'PackageApiStack') {
  new ApiStack(app, 'PackageApiStack', { env });
}
if (ENVIRONMENT.STACK === 'PackageWebStack') {
  new WebStack(app, 'PackageWebStack', { env });
}
