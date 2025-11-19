# CloudFormation

## Page 1

Quy trình cơ bản sử dụng CloudFormation 
1. Chuẩn bị template 
o Viết file YAML/JSON mô tả Resources, Parameters, Mappings, Conditions, 
Outputs, Metadata và Transform nếu dùng modules (macro/Serverless). 
o Tách phần reusable thành nested stacks hoặc modules 
(AWS::CloudFormation::Stack hoặc AWS::Serverless transform). 
2. Kiểm tra template 
o Dùng lệnh CLI: aws cloudformation validate-template --template-body 
file://template.yaml để phát hiện lỗi cú pháp cơ bản. 
o Dùng lint/validator (cfn-lint) để kiểm tra best-practice và định dạng. 
3. Tạo Stack 
o Console: AWS CloudFormation → Create stack → Upload template or use S3 
→ nhập Parameters → Chạy. 
o CLI: aws cloudformation create-stack --stack-name my-stack --template-
body file://template.yaml --parameters ParameterKey=...,ParameterValue=... 
--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM. 
4. Theo dõi tiến trình 
o Console/CLI/CloudFormation Events để xem resource creation events; logs 
chỉ ra lỗi resource failed và nguyên nhân. 
5. Cập nhật Stack 
o Sửa template hoặc thay parameters → aws cloudformation update-stack ... 
o Tạo Change Set (recommended): aws cloudformation create-change-set ... → 
aws cloudformation describe-change-set → aws cloudformation execute-
change-set để xem trước thay đổi và tránh downtime bất ngờ. 
6. Xoá Stack 
o aws cloudformation delete-stack --stack-name my-stack; stack sẽ xoá tất cả 
resources do stack tạo (trừ resources có DeletionPolicy: Retain). 
Cấu trúc template và thành phần chính 
• 
AWSTemplateFormatVersion (tuỳ chọn)

## Page 2

• 
Description — mô tả ngắn. 
• 
Parameters — biến đầu vào (ví dụ: InstanceType, DBPassword); hỗ trợ 
AllowedValues, Default, NoEcho. 
• 
Mappings — bản đồ giá trị cố định (ví dụ: AMI theo region). 
• 
Conditions — điều kiện để tạo resource (ví dụ: CreateProdResources). 
• 
Resources — phần chính; mỗi entry có Type và Properties. 
• 
Outputs — xuất thông tin sau khi tạo stack (ví dụ: LoadBalancerDNS, DBEndpoint). 
• 
Metadata/Transform — cho macro/Serverless transform. 
Ví dụ field Parameter (YAML): 
Parameters: 
  InstanceType: 
    Type: String 
    Default: t3.micro 
    AllowedValues: [t3.micro, t3.small, t3.medium] 
    Description: EC2 instance type 
 
Mẫu kiến trúc tham khảo (tóm tắt) — Web + Backend + DB + ALB 
• 
VPC (public & private subnets) 
• 
Internet Gateway + NAT Gateway 
• 
Security Groups: ALB SG, EC2/ASG SG, RDS SG 
• 
Application Load Balancer (ALB) + Target Group 
• 
Auto Scaling Group (ASG) cho backend (Launch Template/Configuration) 
• 
RDS (Postgres) trong private subnet with Multi-AZ (optional) 
• 
ElastiCache Redis (optional) 
• 
S3 bucket cho static assets + versioning + lifecycle rule 
• 
IAM Roles & Policies cho EC2/Tasks và for CloudFormation (if needed) 
• 
CloudWatch Log Group + Alarms 
• 
Outputs: ALB DNS, RDS endpoint, S3 bucket name

## Page 3

Gợi ý: chia template thành nested stacks: network-stack.yaml, compute-stack.yaml, 
database-stack.yaml, infra-root.yaml (root gọi nested stacks). 
Best practices và governance 
• 
Sử dụng version control cho templates (Git). 
• 
Tách môi trường: dev/staging/prod dùng parameter hoặc separate stacks; tránh 
reuse single prod stack cho dev. 
• 
Dùng Change Sets trước khi apply production change. 
• 
Không lưu secrets plaintext trong Parameters; dùng NoEcho=true + Secrets 
Manager/SSM Parameter Store để inject runtime. 
• 
Sử dụng Capabilities đúng (CAPABILITY_IAM / CAPABILITY_NAMED_IAM) khi tạo 
role/policy. 
• 
Idempotence: thiết kế template để re-apply an toàn; tránh tạo tài nguyên ngoài 
control của stack. 
• 
Rollback on failure: bật để tự rollback khi có lỗi tạo resource (mặc định). 
• 
Resource Protection: set DeletionPolicy (Retain/ Snapshot) cho DB/S3 để tránh mất 
dữ liệu khi delete stack. 
• 
Drift detection: chạy drift detection period để phát hiện thay đổi thủ công trên 
resources. 
CloudFormation trong CI/CD và bảo mật 
• 
Lưu template vào repo; pipeline (GitLab CI / GitHub Actions) validate và tạo change 
set tự động cho branch -> review -> execute on merge to main. 
• 
Sử dụng AWS CloudFormation Change Set trong pipeline để review diffs; require 
manual approval cho production execute. 
• 
Credentials: dùng IAM role for CI (OIDC or AWS role assumption) thay vì static AWS 
keys. 
• 
Logging/Audit: bật CloudTrail và CloudFormation Stack events logging; dùng IAM 
least privilege cho CloudFormation execution role. 
Debugging, lỗi thường gặp và cách xử lý 
• 
Resource creation failed: xem CloudFormation Events để biết lý do; nhiều lỗi do IAM 
permissions, insufficient quotas, invalid parameter value, AMI not found.

## Page 4

• 
Throttling / Quota exceeded: kiểm tra service quotas, tăng quota nếu cần. 
• 
Circular dependencies: chia resources hoặc dùng DependsOn để kiểm soát thứ tự; 
tái cấu trúc nếu lỗi dependency phức tạp. 
• 
Parameter type mismatch: validate template và kiểm tra AllowedValues. 
• 
Stack stuck in UPDATE_ROLLBACK: dùng console/CLI describe-stack-events để tìm 
nguyên nhân; nếu cần, use aws cloudformation continue-update-rollback --stack-
name ... để tiếp tục, hoặc fix template và retry. 
• 
Drift detected: chạy drift detection, sau đó decide migrate template hoặc undo 
manual change. 
Tài nguyên nâng cao và mở rộng 
• 
Nested Stacks: modularize, reuse templates cho networking, DB, app. 
• 
Macros / Transforms: dùng AWS::Serverless transform (SAM) để deploy 
lambda/APIs; CloudFormation Registry & Modules để chia sẻ module. 
• 
Custom Resources: nếu cần thao tác ngoài AWS native, dùng AWS Lambda-backed 
custom resources. 
• 
StackSets: triển khai stack đồng thời trên nhiều accounts/regions (useful cho multi-
account org). 
• 
CloudFormation Registry & Modules: reuse public/private modules (ví dụ module 
VPC, RDS, EKS).
