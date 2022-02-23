_I = 'notebook'
_H = 'StoppingCondition'
_G = 'Outputs'
_F = 'ProcessingInputs'
_E = 'ClusterConfig'
_D = 'ProcessingResources'
_C = 'ProcessingOutputConfig'
_B = None
_A = 'Environment'
import json, os, re, time, boto3


def execute_notebook(*, image, input_path, output_prefix, trigger_time, notebook, parameters, role, instance_type, rule_name,
                     extra_args):
    T = 'LocalPath';
    S = 'S3Uri';
    K = extra_args;
    J = rule_name;
    I = 'AWS_DEFAULT_REGION';
    F = notebook;
    E = output_prefix;
    D = input_path;
    C = role;
    A = image;
    L = ensure_session();
    M = L.region_name;
    N = L.client('sts').get_caller_identity()['Account']
    if not A: A = 'notebook-runner'
    if '/' not in A: A = f"{N}.dkr.ecr.{M}.amazonaws.com/{A}"
    if ':' not in A: A = A + ':latest'
    if not C: C = f"BasicExecuteNotebookRole-{M}"
    if '/' not in C: C = f"arn:aws:iam::{N}:role/{C}"
    if E is _B: E = os.path.dirname(D)
    if F == _B: F = D
    O = os.path.basename(F);
    P, U = os.path.splitext(O);
    G = time.strftime('%Y-%m-%d-%H-%M-%S', trigger_time);
    V = ('papermill-' + re.sub('[^-a-zA-Z0-9]', '-', P))[:62 - len(G)] + '-' + G;
    Q = '/opt/ml/processing/input/';
    W = Q + os.path.basename(D);
    H = '{}-{}{}'.format(P, G, U);
    R = '/opt/ml/processing/output/';
    B = {_F: [{'InputName': _I, 'S3Input': {S: D, T: Q, 'S3DataType': 'S3Prefix', 'S3InputMode': 'File',
                                            'S3DataDistributionType': 'FullyReplicated'}}],
         _C: {_G: [{'OutputName': 'result', 'S3Output': {S: E, T: R, 'S3UploadMode': 'EndOfJob'}}]},
         'ProcessingJobName': V, _D: {_E: {'InstanceCount': 1, 'InstanceType': instance_type, 'VolumeSizeInGB': 40}},
         _H: {'MaxRuntimeInSeconds': 7200}, 'AppSpecification': {'ImageUri': A, 'ContainerArguments': ['run_notebook']},
         'RoleArn': C, _A: {}}
    if K is not _B: B = merge_extra(B, K)
    B[_A]['PAPERMILL_INPUT'] = W;
    B[_A]['PAPERMILL_OUTPUT'] = R + H
    if os.environ.get(I) != _B: B[_A][I] = os.environ[I]
    B[_A]['PAPERMILL_PARAMS'] = json.dumps(parameters);
    B[_A]['PAPERMILL_NOTEBOOK_NAME'] = O
    if J is not _B: B[_A]['AWS_EVENTBRIDGE_RULE'] = J
    X = boto3.client('sagemaker');
    H = X.create_processing_job(**B);
    Y = H['ProcessingJobArn'];
    Z = re.sub('^.*/', '', Y);
    return Z


def merge_extra(orig, extra):
    C = 'KmsKeyId';
    B = extra;
    A = dict(orig);
    A[_F].extend(B.get(_F, []));
    A[_C][_G].extend(B.get(_C, {}).get(_G, []))
    if C in B.get(_C, {}): A[_C][C] = B[_C][C]
    A[_D][_E] = {**A[_D][_E], **B.get(_D, {}).get(_E, {})};
    A = {**A, **{A: C for (A, C) in B.items() if A in ['ExperimentConfig', 'NetworkConfig', _H, 'Tags']},
         _A: {**orig.get(_A, {}), **B.get(_A, {})}};
    return A


def ensure_session(session=_B):
    'If session is None, create a default session and return it. Otherwise return the session passed in';
    A = session
    if A is _B: A = boto3.session.Session()
    return A


def lambda_handler(event, context):
    A = event
    trigger_time = time.gmtime()
    parameters = A.get('parameters', dict())
    for k, v in parameters.items():
        if v == '@trigger_time':
            parameters[k] = time.strftime('%Y-%m-%d %H-%M-%S', trigger_time)
    B = execute_notebook(image=A.get('image'), input_path=A['input_path'],
                         output_prefix=A.get('output_prefix'),
                         trigger_time=trigger_time,
                         notebook=A.get(_I),
                         parameters=A.get('parameters', dict()),
                         role=A.get('role'),
                         instance_type=A.get('instance_type', 'ml.m5.large'),
                         rule_name=A.get('rule_name'),
                         extra_args=A.get('extra_args'))
    return {'job_name': B}
