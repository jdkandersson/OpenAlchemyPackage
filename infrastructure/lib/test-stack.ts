import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as logs from '@aws-cdk/aws-logs';

export class TestStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda function
    const func = new lambda.Function(this, 'Func', {
      functionName: 'test-service',
      runtime: lambda.Runtime.NODEJS_12_X,
      code: lambda.Code.fromInline(
        'exports.handler = function(event, ctx, cb) { throw ("error"); }'
      ),
      handler: 'index.handler',
      logRetention: logs.RetentionDays.ONE_WEEK,
      timeout: cdk.Duration.seconds(5),
    });
    func.logGroup.addMetricFilter('test-error', {
      filterPattern: { logPatternString: 'ERROR' },
      metricName: 'error',
      metricNamespace: 'test-service',
    });
  }
}
