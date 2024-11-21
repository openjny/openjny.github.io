+++
title = "Inside Azure AIOps #2: Incident Management"
slug = "inside-azure-aiops-02-incident-management"
date = "2024-11-15"
categories = [
    "Azure"
]
tags = [
    "AIOps",
    "SRE",
    "DevOps"
]
series = ["Inside Azure AIOps"]
+++

This article is the second installment in the "Inside Azure AIOps" series. This time, I will dive in how Microsoft's been beefing up incident management with AIOps.

{{< notice info "Series" >}}

- [Inside Azure AIOps #1: Introduction]({{<ref "posts/2024-11-11-inside-azure-aiops-01/index.en.md">}})
- [Inside Azure AIOps #2: Incident Management]({{<ref "posts/2024-11-15-inside-azure-aiops-02/index.en.md">}})
- Inside Azure AIOps #3: Resource Management
{{< /notice >}}

## Incident Management and AIOps <!--more-->

### What is Incident Management?

Incident Management is the process of promptly and effectively resolving issues that occur within systems or services. It not only involves resolving the incidents but also identifying their root causes and taking measures to prevent future incidents. Therefore, incident management is an continuous effort and is recognized as a critical process in IT service management.

The typical lifecycle of an incident is as follows:

{{< figure src="icm-flow.en.png" caption="Incident management steps" >}}

| **Step**                      | **Description**                                                                                                                                                                                       |
| :---------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prediction**                | Predicts the occurrence of failures based on observational data. Measures are taken to prevent predicted failures in advance, or plans are prepped to respond if the failure occurs.                  |
| **Detection**                 | Detects ongoing incidents. Incidents are identified through various means such as user reports, monitoring system alerts, and log analysis.                                                           |
| **Triage**                    | Evaluates the severity and impact of the detected incidents, and assigns priorities (priority levels). Additionally, service teams or on-call engineers (OCE) are allocated to resolve the incidents. |
| **Diagnosis**                 | Collects information to consider mitigation strategies. In this step, it is crucial to quickly understand the incident situation, without necessarily identifying the root cause.                     |
| **Mitigation**                | Takes and implements measures to return the system to a stable state. Various methods such as rollback of settings and system reboots are utilized to mitigate the incident.                          |
| **Root Cause Analysis (RCA)** | Identifies the root cause of the incident by investigating monitoring data and codebases. Measures are also taken to prevent the recurrence of the same incident.                                     |
| **Resolution**                | Confirms that the root cause has been resolved through actions like hardware replacement, patch application, or configuration changes, and then closes the incident.                                  |

{{< notice info >}}
Incidents can occur due to various factors such as hardware failures, software bugs, or incorrect user operations. It's important to note that incidents and failures are often confused, but they are distinct concepts. A failure refers to the state where a system's functionality is not operating correctly, while an incident refers to a state where the user is affected.

However, in the context of AIOps, incidents and failures are often not clearly distinguished. This is likely because the primary concern is the normality/abnormality of the system state rather than the presence or absence of user impact. Therefore, in this article as well, we will not particularly differentiate between incidents and failures.
{{< /notice >}}

### Tasks Covered by AIOps

Essentially, the tasks addressed by AIOps correspond to the steps in incident management. For example, detecting early signs of a disk failure tackles the "Prediction" problem. However, even if the focus is on a specific step, it often covers multiple steps in practice. For instance, if the goal is the automation of "Mitigation," the design typically takes into account the "Diagnosis" phase too.

Plus, AIOps also handles more general tasks, such as:

- **Data Preprocessing**: Preprocessing monitoring data to derive important insights (e.g., log filtering, missing data imputation).
- **Incident Correlation**: Discovering similar incidents (e.g., pre-preparation for triage, aggregating support requests stemming from the same failure).
- **Automation**: Streamlining various operations into pipelines for automatic control (e.g., automated execution of troubleshooting tools).
- **User Experience**: Designing a UX that is easy for incident responders to understand (e.g., summarizing failure details using LLMs, establishing verification steps through Human-in-the-Loop).
- **Visualization**: Visualizing data for an intuitive understanding of the system status.

### Common Metrics (KPIs)

The metrics used in incident management include the following:

| Metric   | Full Name             | Description                                                                                               |
| :------- | :-------------------- | :-------------------------------------------------------------------------------------------------------- |
| **MTTD** | Mean Time to Detect   | Average time from the occurrence of an incident to its detection                                          |
| **MTTT** | Mean Time to Triage   | Average time from the detection of an incident to its assignment to the appropriate responder             |
| **MTTM** | Mean Time to Mitigate | Average time from the detection of an incident to its mitigation                                          |
| **MTTR** | Mean Time to Resolve  | Average time from the detection of an incident to its resolution                                          |
| **COGS** | Cost of Goods Sold    | Indicates the direct costs related to delivering a product or service, used in profit margin calculations |

Ultimately, AIOps aims to improve the same metrics, targeting enhancements in indicators like MTTD and MTTM. However, when machine learning models are employed, their predictive performance is also a crucial metric.

## Incident Management at Microsoft

In Microsoft's production environments, incident management follows similar steps described eariler. The overview of an incident's life cycle from detection (prediction) to resolution is as follows.

{{< figure src="icm-flow-in-microsoft.en.png" caption="Incident Management process in production systems at Microsoft" >}}

Incidents are created in response to reports from either users or monitoring systems. All incidents are centrally managed by the Incident Management System (IcM). In IcM, not only are the attributes and descriptions of incidents recorded, but discussions among engineers are also exchanged. Incidents with high priority are promptly assigned to an on-call engineer (OCE), who plays a main role in mitigation. After the symptoms are alleviated, the incident is handed over to a service team for root cause analysis (RCA) and resolution.

AIOps primarily targets the optimization of monitoring systems and IcM systems. The focus is on improving prediction accuracy, preventing false detections and missed detections, and providing more accurate diagnostic information, thereby speeding up the time to mitigation and resolution.

For those interested in more details, please refer to the following papers:

- [An Empirical Investigation of Incident Triage for Online Service Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/an-empirical-investigation-of-incident-triage-for-online-service-systems/)
- [Identifying linked incidents in large-scale online service systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/identifying-linked-incidents-in-large-scale-online-service-systems/)
- [Towards intelligent incident management: why we need it and how we make it - Microsoft Research](https://www.microsoft.com/en-us/research/publication/towards-intelligent-incident-management-why-we-need-it-and-how-we-make-it/)
- [What bugs cause production cloud incidents? - Microsoft Research](https://www.microsoft.com/en-us/research/publication/what-bugs-cause-production-cloud-incidents/)
- [Fast Outage Analysis of Large-scale Production Clouds with Service Correlation Mining - Microsoft Research](https://www.microsoft.com/en-us/research/publication/fast-outage-analysis-of-large-scale-production-clouds-with-service-correlation-mining/)
- [X-Lifecycle Learning for Cloud Incident Management using LLMs | Companion Proceedings of the 32nd ACM International Conference on the Foundations of Software Engineering](https://dl.acm.org/doi/10.1145/3663529.3663861)

## How Microsoft Leverages AIOps in Incident Management

Now, we all set to dive into the main topic. I'll explore the various technologies that have been developed and implemented within Microsoft.

### A New Mitigation Paradigm through Failure Prediction

> "An ounce of prevention is worth a pound of cure."
> —— Benjamin Franklin

By catching early signs of anomalies before failures occur, we can significantly reduce user impact and improve reliability. 

This is precisely why Microsoft has invested years in predictive failure technologies. The initial targets were baremetal servers hosting VMs (nodes) and the disks attached with those nodes, as they are some of the most critical resources to keep VMs running.

{{< figure src="node-disk-prediction.en.png" caption="Node Failure Prediction and Disk Failure Prediction" >}}

- **Node Failure Prediction**: In 2018, the node failure prediction system "MING" was introduced[^ming]. MING stands out by combining deep neural networks with traditional machine learning models, allowing it to handle both temporal data and topological information simultaneously. Data shows that for the top nodes predicted to have high failure rates by MING, 60% failed the next day. Additionally, continuous improvement of node failure prediction models through a method called "Uptake" was developed by 2024[^uptake].
- **Disk Failure Prediction**: In 2018, the disk failure prediction system "CDEF," leveraging SMART data, was deployed[^cdef], and it was refined into "NTAM" in 2021[^ntam]. NTAM improves accuracy by processing information from multiple disks collectively, not just individually. This process has incorporated feature generation techniques using neural networks[^nfs] and methodologies using reinforcement learning to address imbalanced training data[^pulns].

Node and disk failure predictions enable **proactive mitigation actions** based on forecasts. For example, Azure's virtualization platform offers [live migration](https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates#live-migration) that allows VMs on faulty nodes to be moved to healthy ones, minimizing impact (Note: the blackout period is usually just a few seconds[^ml-live-migration]).

As a result, a new Azure virtualization platform management system called "Narya" was introduced in 2020, premised on predictive mitigation[^narya][^intro-narya].

{{< figure src="naraya-architecture.png" caption="Architecture of Narya" >}}

One of the problems Narya addresses is the learning of action policies. It needs mechanisms that adapt behavior depending on the situation (e.g., predicted failure probability, the component where a failure might occur, the number of virtual machines hosted), and that make adjustments from results. This type of problems has been studied within the realm of reinforcement learning, specifically [Multi-Armed Bandit](https://en.wikipedia.org/wiki/Multi-armed_bandit).

These cumulative efforts significantly contribute to reducing VM interruption events and enhancing the reliability of the Azure platform. In terms of AIR (Annual Interruption Rate)[^air], Narya has successfully achieved a 26% improvement over a static action policy.

Lastly, inspired by Narya's success, a similar orchestration system called "F3" was also developed[^f3]. F3 integrates necessary features for proactive mitigation such as drift monitoring, pre-processing log data, augumentating imbalanced data, and learning action policies based on Reinforcement Learning techniques.

{{< notice tip "Takeaway" >}}
By utilizing node/disk failure prediction and the Narya management system powered by Reinforcement Learning techniques, Microsoft has significantly reduced VM interuptions and enhanced the reliability of the Azure platform.
{{< /notice >}}

[^air]: AIR (Annual Interruption Rate) for VM is defined as the average number of interruptive events on 100 VMs over one year.
[^ming]: [Predicting Node Failure in Cloud Service Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/predicting-node-failure-in-cloud-service-systems/)
[^uptake]: [Can We Trust Auto-Mitigation? Improving Cloud Failure Prediction with Uncertain Positive Learning - Microsoft Research](https://www.microsoft.com/en-us/research/publication/can-we-trust-auto-mitigation-improving-cloud-failure-prediction-with-uncertain-positive-learning/)
[^cdef]: [Improving Service Availability of Cloud Systems by Predicting Disk Error - Microsoft Research](https://www.microsoft.com/en-us/research/publication/improving-service-availability-cloud-systems-predicting-disk-error/)
[^ntam]: [NTAM: Neighborhood-Temporal Attention Model for Disk Failure Prediction in Cloud Platforms - Microsoft Research](https://www.microsoft.com/en-us/research/publication/ntam-neighborhood-temporal-attention-model-for-disk-failure-prediction-in-cloud-platforms/)
[^nfs]: [Neural Feature Search: A Neural Architecture for Automated Feature Engineering | IEEE Conference Publication | IEEE Xplore](https://ieeexplore.ieee.org/document/8970679?denied=)
[^pulns]: [PULNS: Positive-Unlabeled Learning with Effective Negative Sample Selector | Proceedings of the AAAI Conference on Artificial Intelligence](https://ojs.aaai.org/index.php/AAAI/article/view/17064)
[^ml-live-migration]: [Improving Azure Virtual Machine resiliency with predictive ML and live migration | Microsoft Azure Blog](https://azure.microsoft.com/en-us/blog/improving-azure-virtual-machine-resiliency-with-predictive-ml-and-live-migration/)
[^narya]: [Narya: Predictive and Adaptive Failure Mitigation to Avert Production Cloud VM Interruptions - Microsoft Research](https://www.microsoft.com/en-us/research/publication/predictive-and-adaptive-failure-mitigation-to-avert-production-cloud-vm-interruptions/)
[^intro-narya]: [Advancing failure prediction and mitigation—introducing Narya | Azure Blog | Microsoft Azure](https://azure.microsoft.com/es-es/blog/advancing-failure-prediction-and-mitigation-introducing-narya/)
[^f3]: [F3: Fault Forecasting Framework for Cloud Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/f3-fault-forecasting-framework-for-cloud-systems/)

### Quality Assurance for GPU Nodes

Recently, Microsoft has been doubling down its AI infrastructure, which includes components like GPUs, NPUs, and high-speed interconnects[^build23-brk290][^build24-brk256][^ocpsummit24-ai-infra][^blog-20241015-dc].

As implementing it, Microsoft has faced a unique set of challenges, one of wich is that GPU nodes are prone to failures. The potential causes for these failures may include:

- 📉 **Hardware Regression**: AI-centric processors are released every 1-2 years, and there might not be enough regression testing conducted. Simple micro-benchmarks (e.g., [GEMM](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html), [NCCL Tests](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html)) might not catch all regressions that manifest only under specific workloads.
- ⚖️ **Differences in Environments**: The conditions in vendor test environments differ from those in cloud data centers, particularly regarding factors like power and temperature. For example, Microsoft's data centers have observed that the number of abnormal InfiniBand links, exceeding the bit error rate required by the specification (10E-12), is 35 times higher in tropical regions. As such, environments play a huge role in diverse failure patterns.
- 👶🏻 **Immature Software Stacks**: As hardware evolves, the application layers need to be updated as well. Software stacks like CUDA or ROCm release new versions every few months, making it challenging to maintain a highly reliable stack.

Moreover, the nature of AI infrastructure, with high redundancy across various layers (e.g., row-remapping in NVIDIA GPUs[^row-remapping]), often leads to gray failures and complex and time-consuming troubleshooting.

{{< notice info >}}
A [gray failure](https://www.usenix.org/conference/srecon24americas/presentation/li) refers to partial failures that are so subtle they are hard to detect. Fault-tolerant systems have redundancy measures to handle partial failures. In the event of a partial failure, the system might switch to a degraded mode where performance and availability are not fully maintained. If the monitoring systems or applications can detect performance degradation, they can explore mitigations, thus limiting the risk. However, if the failure is too subtle to detect, the state of "it should be fine, but isn’t" persists, potentially escalating into a cascading failure. Sometimes it's called [Limplock](https://dl.acm.org/doi/10.1145/2523616.2523627) when focusing on its performance degradation aspect.
{{< /notice >}}

Thus, it is preferred to prevent failures before they occur, one method being **Quality Assurance (QA)**. QA involves running benchmark tests to check the health of nodes before they are deployed in production. However, given the countless AI workload patterns and the high cost of infrastructure, running comprehensive benchmark tests is impractical.

This is where **"SuperBench"**[^superbench] comes into play. It is a system introduced in 2024, designed to effectively eliminate aberrant GPU nodes before deploying them, through a combination of machine learning and benchmarking.

{{< figure src="superbench-architecture.en.png" caption="SuperBench Execution Flow" >}}

Given some nodes to be tested, SuperBench first predicts the risk of failure with a statistical model called Cox-Time. If the risk is deemed high, the system selects the most appropriate set of benchmarks to identify potential node issues. While it is not trivial to select the thresholds for each benchmark, SuperBench uses machine learning models to derive baseline values. It then evaluates the benchmark results for anomalies and outputs a final  decision (go/no-go for each node).

SuperBench is already operational in Azure's production environment and has identified issues in approximately 10% of nodes before production deployment within two years of operations.

{{< notice tip "Takeaway" >}}
SuperBench is a system that predicts and eliminates abnormal GPU nodes before deployment through a mix of machine learning and benchmarking. It has already identified issues in approximately 10% of nodes before production deployment within two years of operations.
{{< /notice >}}

[^build23-brk290]: [Inside Azure innovations with Mark Russinovich | BRK290HFS](https://www.youtube.com/watch?v=sgIBC3yWa-M)
[^build24-brk256]: [Inside Microsoft AI innovation with Mark Russinovich | BRK256](https://www.youtube.com/watch?v=ntKZ5CibuIQ)
[^ocpsummit24-ai-infra]: [Exploring the Inner Workings of Azures Advanced AI Infrastructure Presented by Microsoft](https://www.youtube.com/watch?v=l6LptgXMjsY)
[^blog-20241015-dc]: [Accelerating industry-wide innovations in datacenter infrastructure and security | Microsoft Azure Blog](https://azure.microsoft.com/en-us/blog/accelerating-industry-wide-innovations-in-datacenter-infrastructure-and-security/)
[^row-remapping]: [1. Overview — NVIDIA GPU Memory Error Management r555 documentation](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html#row-remapping)
[^superbench]: [SuperBench: Improving Cloud AI Infrastructure Reliability with Proactive Validation - Microsoft Research](https://www.microsoft.com/en-us/research/publication/superbench/)

### Practical Alert System Incorporating Machine Learning

Fault detection is a challenging task because there are countless "anomalous" patterns in a system, making it difficult to accurately define alert rules.

At Microsoft, despite years of operating online services and continuous efforts, both false positives (detected but did not require action)[^alert-fatigue] and miss-detections (failures in detecting an issue before it impacts) occur at a consistent frequency[^esec23-parayil]. Additionally, it was understood that a major reason for detection misses was the inadequacy of alert rules, highlighting the difficulties in defining what constitutes an "anomaly."

Given this backdrop, machine learning approaches have been actively researched, and in recent years, anomaly detection models using deep neural networks for time series data have garnered attention[^aiops-anomaly-detection-survey]. However, despite academic success, these models have not been extensively applied in practice. Microsoft has summarized the reasons for this into the following three points:

- **Selection of models and hyperparameters**: The optimal model varies depending on the nature of the time series data, so it is necessary to choose the best model for the workload being monitored. Additionally, the model's hyperparameters need to be determined. When dealing with numerous metrics, manual selection is unrealistic.
- **Interpretation of anomalies**: Some fluctuations in metrics might be considered faults, while others might not. Practical fault detection requires a mechanism to identify and manage the waveform patterns considered "anomalous" from a service perspective, but existing models usually do not provide such interpretability.
- **Handling data drift**: Models need to be continually updated as the characteristics of the data change. However, only a limited number of engineers (e.g., data scientists) can retrain the models, and service teams cannot provide feedback.

To overcome these challenges, a practical metric-based fault detection system called "MonitorAssistant" was introduced[^monitorassistant].

{{< figure src="monitor-assist-architecture.png" caption="Architecture of MonitorAssistant" >}}

MonitorAssistant registers machine learning models in advance like a catalog and suggests the optimal model for a given metric. To enhance model interpretability, it can classify anomaly categories (e.g. sudden spike). Furthermore, service teams can firsthand give feedback through a chatbot (LLM) to adjust the model in case of false detactions or misses, without involving data scientists in the loop.

{{< figure src="monitor-assistant-example.png" caption="Example report generated by MonitorAssistant" >}}

[^esec23-parayil]: [Detection Is Better Than Cure: A Cloud Incidents Perspective - Microsoft Research](https://www.microsoft.com/en-us/research/publication/detection-is-better-than-cure-a-cloud-incidents-perspective/)
[^alert-fatigue]: [Anti-Patterns of System Operations - Solving Organizational, Automation, and Communication Problems with DevOps](https://www.oreilly.co.jp//books/9784873119847/)'.
[^aiops-anomaly-detection-survey]: [[2308.00393] A Survey of Time Series Anomaly Detection Methods in the AIOps Domain](https://arxiv.org/abs/2308.00393)
[^monitorassistant]: [MonitorAssistant: Simplifying Cloud Service Monitoring via Large Language Models - Microsoft Research](https://www.microsoft.com/en-us/research/publication/monitorassistant-simplifying-cloud-service-monitoring-via-large-language-models/)

{{< notice tip "Takeaway" >}}
Microsoft has developed MonitorAssistant, a practical metric-based fault detection system that suggests optimal machine learning models for metrics, provides anomaly classification, and allows service teams to adjust models through a chatbot.
{{< /notice >}}

### Exploring Effective Attributes of Multidimensional Data

When utilizing metrics, the use of **attributes** (aka dimensions[^attribute]) is crucial, as you will end up with different outcomes depending on how to filter metrics on those attributes.

Consider a management system that collects incident reports from servers worldwide. These reports are tagged with various attributes such as server name, data center name, customer, and country. Suppose a service for educational customers deployed in the 6th data center in India went down.

{{< figure src="effective-attributes.png" caption="The number of incidents filtered by attributes (country, customer type, data center) over time" >}}

If you have an appropriate attribute set to filter out as in the figure above, you should be able to clearly see an increase in incidents. However, if you view the same time-series data without filtering by attributes, the incidents reported from all over the world would be leveled out, making it difficult to pinpoint any anomalies.

Thus, in multivariate data anomaly detection, exploring such an effective set of attributes for filtering is crucial. Typically, this task is performed iteratively by humans, but as the number of attributes grows, it becomes unmanageable due to combinatorial explosion.

To address this, Microsoft approached the exploration of effective attributes as a tree structure search problem where nodes represent combinations of attributes, and developed an incident detection system called "iDice"[^idice]. Additionally, in 2020, they tackled a new method (MID) to reduce the search space using metaheuristics[^mid]. These outcomes have been successfully applied in Azure as AiDice[^aidice].

{{< figure src="effective-attributes-fault.png" caption="Example of using attribute exploration for fault identification" >}}

There's a similar initiative dubbed "HALO"[^halo]. HALO targets any multidimensional metrics associated with servers (e.g. API call failure counts) and identifies attribute sets where anomalies (server faults) are occurring. What's unique about HALO is it can take into account the topological information of servers in datacenters. HALO has been implemented in Azure's Safe Deployment management system (Gandalf[^gandalf]) to detect deployment issues when rolling updates or fixes to canary/production environments.

{{< notice tip "Takeaway" >}}
In the Azure ecosystem, effective attributes (dimensions) are crucial for filtering metrics. Microsoft has developed a system called AiDice to explore effective attributes for incident detection, and HALO to identify attribute sets where anomalies are occurring.
{{< /notice >}}

[^attribute]: In the Azure ecosystem, these are referred to as [dimensions](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-platform-metrics#multi-dimensional-metrics).
[^idice]: [iDice: Problem Identification for Emerging Issues - Microsoft Research](https://www.microsoft.com/en-us/research/publication/idice-problem-identification-emerging-issues/)
[^mid]: [Efficient incident identification from multi-dimensional issue reports via meta-heuristic search - Microsoft Research](https://www.microsoft.com/en-us/research/publication/efficient-incident-identification-from-multi-dimensional-issue-reports-via-meta-heuristic-search/)
[^aidice]: [Advancing anomaly detection with AIOps—introducing AiDice | Microsoft Azure Blog](https://azure.microsoft.com/en-us/blog/advancing-anomaly-detection-with-aiops-introducing-aidice/)
[^halo]: [HALO: Hierarchy-aware Fault Localization for Cloud Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/halo-hierarchy-aware-fault-localization-for-cloud-systems/)
[^gandalf]: [Advancing safe deployment with AIOps—introducing Gandalf | Microsoft Azure Blog](https://azure.microsoft.com/en-us/blog/advancing-safe-deployment-with-aiops-introducing-gandalf/)

### Responding to Outages

Incidents with a significant impact on a number of services and users are referred to as **outages**, and one of the important steps to tackle them is **identification**. While one can suspect an outage if similar reports come in from multiple users, significant time may have already passed by that time. It is more preffered to systematically detect outages early on, without waiting for user reports.

{{< figure src="airalert-outage.png" caption="Left: Bayesian network constructed by AirAlert, Right: Trends of metrics deemed related" >}}

To achieve this, the following two siblings were born:

- Microsoft first developed "AirAlert," a method for detecting outages using Bayesian networks[^airalert]. It applys a causal inference method to model the dependencies between the alerting signals and outage as a directed acyclic graph (DAG). This allows for extracting the set of signals most related to the outage, thus inferring the occurrence of an outage.
- Furthermore, a new detection method called "Warden" was introduced for the higher accuracy[^warden]. While AirAlert only utilizes the number of alerts when constructing a DAG, Warden can factor in diverse information such as OCEs' discussions, achieving substantial performance improvement.

Once an outage has been identified, engineers move to the investigation phase, for which Microsoft has introduced a supporting tool called "Oasis" in 2023[^oasis].

{{< figure src="oasis-overview.png" caption="Flow of Oasis scoping and summarizing an outage" >}}

Oasis is a system that identifies the impact scope of an outage by linking relevant incidents and generates summaries using LLMs. Oasis enhances accuracy by using three different linking methods in combination:

- **Rule-based linking**: Leveraging the domain knowledge of engineers
- **Component dependency-based linking**: Utilizing service or topological dependencies between components previously associated in past outages
- **Machine learning model-based linking**: Employing machine learning models to predict links between incidents, such as LiDAR[^lidar] or LinkCM[^linkcm]

Finally, here is a sample summary generated by Oasis. It provides sufficient information to easily understand the content of the outage, the services impacted, and its severity.

> **Outage Summary by Oasis**: The API failed with HTTP 5xx errors (over 𝛼_1 fall failures) because of bad gateway errors to the endpoint_1. Due to this issue, commercial customers could not sign-up for System-Cloud or SystemProductivity via endpoint_2 or endpoint_3, and perform management related actions on endpoint_4. Additionally, System-Cloud users were not able to access their billing accounts and invoices on System-Cloud portal. Approximately 𝛼_2 unique users were impacted.

{{< notice tip "Takeaway" >}}
Microsoft has developed Bayesian network-based approaches for outage detection, called AirAlert and Warden, and Oasis for scoping and summarizing outages. Oasis uses a combination of three incident linking methods to enhance accuracy.
{{< /notice >}}

[^airalert]: [Outage Prediction and Diagnosis for Cloud Service Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/outage-prediction-and-diagnosis-for-cloud-service-systems/)
[^warden]: [Fighting the Fog of War: Automated Incident Detection for Cloud Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/fighting-the-fog-of-war-automated-incident-detection-for-cloud-systems/)
[^oasis]: [Assess and Summarize: Improve Outage Understanding with Large Language Models - Microsoft Research](https://www.microsoft.com/en-us/research/publication/assess-and-summarize-improve-outage-understanding-with-large-language-models/)
[^lidar]: [Identifying linked incidents in large-scale online service systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/identifying-linked-incidents-in-large-scale-online-service-systems/)

### Improving Triage Efficiency

Reflecting on the history of incident triage in Microsoft takes us back to the days of online services before Azure's birth (e.g. Office 365, Skype).

Back then, when an incident was created, the system would make phone calls to multiple on-call engineers. Engineers would manually assess the priority and assign the appropriate response teams[^icse19-triage]. This method consumed a lot of engineers' efforts and loads, highlighting the need for an automated triage system.

The first attempt was to repurpose existing methods that automatically assign bug reports to software engineers[^icse19-triage]. While this approach demonstrated some applicability, the fundamental differences between bug reports and online service incidents concluded that a method tailored to online services was necessary. Subsequently, the following endeavors were explored:

- **In 2019**: A continuous incident triage system called "DeepCT" was proposed[^deepct]. Considering that the assignment of incidents could occur multiple times as investigations progressed, DeepCT learned from engineers' discussions and continuously updated the triage results.
- **In 2020**: An improved system over DeepCT, called "DeepTriage," was deployed in production[^deeptriage]. While DeepCT relied on a deep neural network to classify the responsible team, DeepTriage enhanced accuracy using an ensemble of multiple models, including LightGBM[^lightgbm] developed by Microsoft.
- **In 2020**: A method named "DeepIP" was proposed to filter out alerts that did not require action (false positives) and adjust their priority[^deepip]. In this study, preliminary research revealed that over 30% of the alerts were false positives, and a deep learning-based prioritization was implemented.
- **In 2021**: A prediction method called "TTMPred" was proposed to estimate the time required to mitigate an incident (TTM), enabling appropriate personnel allocation[^ttmpred]. TTMPred used recurrent neural networks (RNNs) to capture the progression of discussions and text information.

The latest development is the proposal of a new incident triage system called "COMET" in 2024, which leverages LLMs[^comet].

{{< figure src="comet-overview.png" caption="Architecture of COMET" >}}

One of COMET's notable features is its effective handling of logs during triage. Logs of components related to the incident contain crucial information needed for triage, but handling these logs with machine learning models requires addressing original challenges such as trimming redundant logs, extracting important keywords, and dealing with data imbalances. COMET tackles these issues using a mix of existing log processing engines and LLMs (w/ In-Context Learning).

Additionally, COMET provides a feature to report analysis results along with incident triage. In an actual incident management system, analysis results by COMET are presented as follows:

{{< figure src="comet-example.en.png" height=400 caption="Report presented to on-call engineers by COMET" >}}

This exemplifies how COMET is not just a triage system but also provides critical insights. Performance evaluation has shown a 30% improvement in triage accuracy and up to a 35% reduction in TTM (Time-To-Mitigate). COMET is currently in operational use for internal services offering virtual machines.

{{< notice tip "Takeaway" >}}
Microsoft has developed a series of incident triage systems, including DeepCT, DeepTriage, DeepIP, TTMPred, and COMET. COMET, the latest system, leverages LLMs and effectively handles logs during triage, providing critical insights to on-call engineers.
{{< /notice >}}

[^icse19-triage]: [An Empirical Investigation of Incident Triage for Online Service Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/an-empirical-investigation-of-incident-triage-for-online-service-systems/)
[^deepct]: [Continuous incident triage for large-scale online service systems | Proceedings of the 34th IEEE/ACM International Conference on Automated Software Engineering](https://dl.acm.org/doi/10.1109/ASE.2019.00042)
[^deeptriage]: [DeepTriage | Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining](https://dl.acm.org/doi/abs/10.1145/3394486.3403380)
[^deepip]: [How incidental are the incidents? | Proceedings of the 35th IEEE/ACM International Conference on Automated Software Engineering](https://dl.acm.org/doi/10.1145/3324884.3416624)
[^ttmpred]: [How Long Will it Take to Mitigate this Incident for Online Service Systems? - Microsoft Research](https://www.microsoft.com/en-us/research/publication/how-long-will-it-take-to-mitigate-this-incident-for-online-service-systems/)
[^comet]: [Large Language Models Can Provide Accurate and Interpretable Incident Triage - Microsoft Research](https://www.microsoft.com/en-us/research/publication/large-language-models-can-provide-accurate-and-interpretable-incident-triage/)
[^lightgbm]: [Welcome to LightGBM’s documentation! — LightGBM 4.5.0 documentation](https://lightgbm.readthedocs.io/en/stable/)

### Linking Associated Incidents

Identifying and linking similar incidents is beneficial in many aspects of incident response. For instance:

- Due to dependencies between services, incidents can cascade and spread across components (known as cascading failure).
- The same issue can trigger mutiple alerts or be reported by multiple customers.
- Related past incidents can provide crucial hints during investigation.

Microsoft has devised and implemented various methods for incident association.

In 2020, Microsoft introduced "LiDAR," an incident association system for online services inspired by methods used to detect duplicate software bug reports[^lidar]. LiDAR uniquely considers both the textual information of incidents and dependencies between components. Using neural network-based techniques, it extracts features from both sources of information to calculate similarities between incidents.

The same year, a method called "LinkCM" was proposed for associating customer-reported incidents (CI) with incidents automatically logged by monitoring systems (MI)[^linkcm]. This was motivated by the fact that while 77% of CI had corresponding MI logged beforehand, only about 20% were correctly associated early in the investigation. LinkCM interprets the descriptions in natural language from CI and uses deep learning-based methods to link them with MI.

{{< figure src="dilink-overview.png" caption="DiLink Architecture" >}}

In 2024, a new incident association system called "DiLink" was proposed, evolving from LiDAR[^lidar]. Both LiDAR and DiLink utilize textual information and dependency graphs between components as features. However, while LiDAR learned these features using separate models, DiLink achieves more accurate, multimodal incident association by handling textual and dependency graph information in a single neural network.

[^linkcm]: [Efficient customer incident triage via linking with system incidents | Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering](https://dl.acm.org/doi/10.1145/3368089.3417061)

### Generation of KQL Queries

In Microsoft's monitoring systems, it's common to issue queries using a domain-specific language called [Kusto Query Language (KQL)](https://learn.microsoft.com/en-us/kusto/query/).

Troubleshooting using KQL is not an easy task. Engineers need to learn the KQL syntax[^kusto100knocks] and become familiar with the data schema they are looking into. Even with troubleshooting guides, these may be outdated or ineffective for unknown issues. Thus, on-call engineers frequently find themselves having troubles with KQL.

To address this, a system named **"Xpert"** was developed to automatically generate KQL queries[^xpert]. Integrated into the incident management system, Xpert automatically collects information from similar past incidents and generates new KQL queries based on queries used during previous responses. This generation process leverages the context-based learning capabilities of large language models (LLMs) via few-shot learning.

Additionally, the generated KQL queries are designed to maximize a unique metric called Xcore, which is a quality evaluation metric for queries (or code) that can be applied to any DSL. It assesses the quality of queries based on multiple perspectives such as syntactic and semantic accuracy, the correctness of tokens and operations, and the comprehensiveness of information necessary for the investigation.

{{< figure src="xpert-overview.png" caption="Architecture of Xpert " >}}

Xpert adopts an architecture similar to general RAG (Retrieval-Augmented Generation) systems but with a notable post-validation process. In the post-processing phase, the LLM-generated query is validated by parsing to ensure it adheres to KQL syntax. If an incomplete query is generated, the system retries by querying the LLM again for corrections. Moreover, the database that stores incident information and past queries is continuously updated, improving accuracy over time and addressing data drift issues.

[^kusto100knocks]: If you want to learn how to write KQL, "Kusto 100 Knocks" is recommended. Reference: [KUSTO 100+ knocks](https://azure.github.io/fta-kusto100knocks/)
[^xpert]: [Xpert: Empowering Incident Management with Query Recommendations via Large Language Models - Microsoft Research](https://www.microsoft.com/en-us/research/publication/xpert-empowering-incident-management-with-query-recommendations-via-large-language-models/)

{{< notice tip "Takeaway" >}}
Xpert is a system that automatically generates KQL queries for incident management using LLMs. It leverages context-based learning capabilities and a unique quality evaluation metric called Xcore to ensure the generated queries are accurate and comprehensive.
{{< /notice >}}

### Automating Troubleshooting Guides

A team at Microsoft working on hybrid cloud products faced challenges with their troubleshooting guides (TSGs): their TSGs were excessively long (a median of 815 words, with some extending up to 5000 words!). While the automation of TSGs was considered, automating codes or scripts requires maintenance with every TSG update. This team had a high frequency of TSG updates, averaging every 19 days, making it difficult to implement full automation.

To address this, a system named **"LLexus"** was introduced to interpret and execute TSGs written in natural language, powered by LLMs[^llexus]. It is much like the Java runtime, compiling TSGs into the middle language (plans) that can be executed by the LLexus Executor when an incident occurs.

{{< figure src="llexus-overview.png" caption="Architecture of LLexus (figure extracted from the paper)" >}}

An interesting aspect of LLexus is its separation of the **Planner** and **Executor**. When the Planner detects an update to a TSG, it interprets the content with LLMs (combining a technique called Chain of Though) and converts it into an executable plan for the Executor. When an incident occurs and the relevant TSG matches, the plan is executed by the Executor.

This two phase model reduces the cost of invoking LLMs, as there are a greater number of incidents than TSG updates and LLM calls are only made when a TSG is updated. Moreover, LLexus incorporates a Human-in-the-Loop mechanism, where feedback from engineers is immediately given whenever a plan is created from an updated TSG. Plus, by virtue of the fact that incomprehensible and verbose TSGs are likley to fail in being compilied, engineers are incentivized to create more concise and understandable TSGs, bringing benefits to both the system and the engineers.

{{< notice tip "Takeaway" >}}
LLexus is a system that interprets and executes troubleshooting guides written in natural language, powered by LLMs. It separates the Planner and Executor, reducing the cost of invoking LLMs and incorporating a Human-in-the-Loop
{{< /notice >}}

[^llexus]: [LLexus: an AI agent system for incident management - Microsoft Research](https://www.microsoft.com/en-us/research/publication/llexus-an-ai-agent-system-for-incident-management/)

### Root Cause Analysis with LLM

A Microsoft team working on an email delivery service, which sends 150 billion messages daily, needed to optimize their root cause analysis flow for the frequently occurring incidents. After analyzing all incidents from a year, they derived the following insights:

- **Insight 1**: It is difficult to identify the root cause using a single data source.
- **Insight 2**: Incidents stemming from the same or similar root causes have temporal correlations (if they recur, it usually happens within a short timeframe).
- **Insight 3**: A significant number of incidents arise from new root causes, with approximately 25% of incidents being novel phenomena.

Particularly important is Insight 3, indicating that for 25% of incidents, existing troubleshooting guides (TSGs) are not very effective.

To assist with root cause analysis, an AI-assisted system called **"RCACopilot"** was developed[^rcacopilot]. Despite having "Copilot" in its name and implying extensive use of LLMs, it is actually a well-designed automation system where LLM only plays a limited role in summarizing logs.

{{< figure src="rcacopilot-overview.png" caption="Architecture of RCACopilot" >}}

The system follows the following stages:

- When RCACopilot recognizes an incident, it starts with the **information gathering stage**.
  - Adhering to Insight 1, it collects information from as many data sources as possible. A predefined logic flow, registered in advance similar to a directed acyclic graph, guides the data collection process (e.g., collect this log, then run this command, then conditionally branch…). Engineers can modify these flows anytime.
- After information gathering, the system moves to the **root cause prediction stage**.
  - This stage involves searching for similar past incidents. Embeddings obtained using FastText and the time intervals between incidents (based on Insight 2) are used to compute the similarity between incidents.
  - Finally, the system leverages LLM. Since the root causes of past incidents are known, this information is passed as prompts to the LLM, asking, "Here are the logs for the current incident, along with logs and root causes of similar past incidents. Please determine which root cause corresponds to the current incident, or state if none apply, with reasons." The response provided by the LLM is output as the final root cause analysis.

As of 2024, RCACopilot has been in use for over four years across more than 30 service teams. Despite defining information gathering flows being somewhat labor-intensive, many on-call engineers (OCEs) reported high satisfaction in surveys. This satisfaction can be attributed to the ability to save and reuse information gathering logic.

[^rcacopilot]: [Automatic Root Cause Analysis via Large Language Models for Cloud Incidents - Microsoft Research](https://www.microsoft.com/en-us/research/publication/automatic-root-cause-analysis-via-large-language-models-for-cloud-incidents/)

{{< notice tip "Takeaway" >}}
RCACopilot is an AI-assisted system for root cause analysis that leverages LLMs for summarizing logs. It follows a structured flow of information gathering and root cause prediction, with LLMs providing the final root cause analysis.
{{< /notice >}}

### Effective Utilization of Logs and Traces

Finally, let me introduce some approaches for utilizing logs. When handling logs in AIOps, you need to address the following challenges:

- **Large Data Volume**: The amount of log data generated by monitoring systems can reach hundreds of terabytes per day. To use logs for near-real-time incident response, data processing algorithms and pipeline infrastructures with the same throughput as ingestion are required.
- **Difficulty in Parsing Logs**: Parsing logs involves breaking down log messages into the templates and parameters used to generate them. This is akin to predicting the code that produced the message. Effective log parsing requires appropriate log clustering methods.
- **Severe Data Imbalance**: Training data for anomaly prediction models needs to include balanced data from both "normal" and "abnormal" times. However, abnormal data is typically extremely scarce, necessitating strategies (e.g., sampling) to address this imbalance.

From the perspective of reducing data volume, **"Log2"**, presented in 2015, is quite intriguing[^log2]. Log2 provides basic APIs (Begin and End) to measure the execution time of certain processes. This API records data only if the measured time significantly deviates from past measurements, minimizing unnecessary data recording.

In the following year, an incident linking system called **"LogCluster"** was introduced and its log processing technique is interesting[^logcluster]. Assuming that even a vast number of log sequences are actually derived from a limited number of codes, it aggregates logs into clusters (conceputually corresponding to codes) and extracts the representative values of those clusters.

The idea of clustering logs is also seen in other methods. For example, the 2018 method **"Log3C"**[^log3c] and the 2021 method **"Onion"**[^onion] extract log clusters and then apply methods such as correlation analysis and symmetry analysis to detect anomalies and extract anomaly-related log data.

{{< figure src="onion-overview.png" caption="Onion Architecture" >}}

For log parsing, there are two notable methods introduced in 2022 by Microsoft:

- **UniParser**: A log parsing method using deep neural networks[^uniparser]. It uses an LSTM-based Token Encoder to learn log embeddings while combining contrastive loss with similar and dissimilar logs. This enables the acquisition of embeddings considering the semantics of each token and allows for fast inference.
- **SPINE**: A log parsing method designed to be executed in parallel in a distributed computing environment[^spine]. It uses a greedy bin-packing algorithm called "BestFit" to ensure an even distribution of workload (log sets) to the workers executing the jobs. Additionally, it addresses the diversification of logs driven by recent deployments of CI/CD by designing a model retraining loop based on feedback.

Lastly, let's also introduce a method that effectively utilizes traces in addition to logs. A trace is a log taken to allow retrospective tracking of events processed across multiple components. "TraceLingo," proposed in 2021, leverages the fact that such traces can be represented as call trees (tree structures), using a deep neural network model to identify areas (spans) where anomalies occur[^tracelingo].

{{< notice tip "Takeaway" >}}
Microsoft has developed various methods for effectively utilizing logs and traces in AIOps. These methods include Log2 for reducing data volume, LogCluster for log clustering, and Onion for log clustering-based anomaly detection. Additionally, UniParser and SPINE were proposed for log parsing, and TraceLingo for trace representation and learning.
{{< /notice >}}

[^log2]: [Log2: A Cost-Aware Logging Mechanism for Performance Diagnosis - Microsoft Research](https://www.microsoft.com/en-us/research/publication/log2-cost-aware-logging-mechanism-performance-diagnosis-2/)
[^logcluster]: [Log Clustering based Problem Identification for Online Service Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/log-clustering-based-problem-identification-online-service-systems-2/)
[^log3c]: [Identifying Impactful Service System Problems via Log Analysis - Microsoft Research](https://www.microsoft.com/en-us/research/publication/identifying-impactful-service-system-problems-via-log-analysis/)
[^onion]: [Onion: Identifying Incident-indicating Logs for Cloud Systems - Microsoft Research](https://www.microsoft.com/en-us/research/publication/onion-identifying-incident-indicating-logs-for-cloud-systems/)
[^uniparser]: [UniParser: A Unified Log Parser for Heterogeneous Log Data - Microsoft Research](https://www.microsoft.com/en-us/research/publication/uniparser-a-unified-log-parser-for-heterogeneous-log-data/)
[^spine]: [SPINE: A Scalable Log Parser with Feedback Guidance - Microsoft Research](https://www.microsoft.com/en-us/research/publication/spine-a-scalable-log-parser-with-feedback-guidance/)
[^tracelingo]: [TraceLingo: Trace representation and learning for performance issue diagnosis in cloud services | IEEE Conference Publication | IEEE Xplore](https://ieeexplore.ieee.org/document/9527009)

## Approaches Not Fully Covered

There are many other approaches that could not be introduced in detail in this article due to various reasons, such as not being explicitly mentioned as deployed in production, being of lower importance, or myself not fully reading them. This list is likely only a portion, but if you are interested, please check them out.

| Year | Project Name and Link                                                                                                                                                          | Description                                                                                                                                                                                                                                              |
| :--- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2012 | [(Link Only)](https://www.microsoft.com/en-us/research/publication/performance-issue-diagnosis-for-online-service-systems/)                                                    | System to detect performance issues in online services using data mining methods                                                                                                                                                                         |
| 2012 | [NetPilot](https://www.microsoft.com/en-us/research/publication/netpilot-automating-datacenter-network-failure-mitigation/)                                                    | System to detect and safely automatically mitigate data center network failures                                                                                                                                                                          |
| 2014 | [HMRF](https://www.microsoft.com/en-us/research/publication/identifying-recurrent-unknown-performance-issues-2/)                                                               | Method to detect performance issues from metrics                                                                                                                                                                                                         |
| 2017 | [CorrOpt](https://www.microsoft.com/en-us/research/publication/understanding-mitigating-packet-corruption-data-center-networks/)                                               | Monitoring system for detecting packet corruption in data center networks                                                                                                                                                                                |
| 2017 | [GraphWeaver](https://arxiv.org/pdf/2406.01842)                                                                                                                                | Incident association method implemented in [Microsoft Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/investigate-incidents)                                                                                                                |
| 2018 | [Panorama](https://www.microsoft.com/en-us/research/publication/capturing-and-enhancing-in-situ-system-observability-for-failure-detection/)                                   | Monitoring system to detect partial failures and performance degradations like gray faults and limplock                                                                                                                                                  |
| 2019 | [ATAD](https://www.microsoft.com/en-us/research/publication/cross-dataset-time-series-anomaly-detection-for-cloud-systems/)                                                    | Transfer learning anomaly detection model for telemetry with scarce training data                                                                                                                                                                        |
| 2019 | [BlameIt](https://www.microsoft.com/en-us/research/publication/zooming-in-on-wide-area-latencies-to-a-global-cloud-provider/)                                                  | Monitoring system to identify WAN latency issues and their causes (ISP or WAN)                                                                                                                                                                           |
| 2019 | [NetBouncer](https://www.usenix.org/conference/nsdi19/presentation/tan)                                                                                                        | Monitoring system to detect link failures (device failures) within data center networks                                                                                                                                                                  |
| 2019 | [SR-CNN](https://arxiv.org/pdf/1906.03821)                                                                                                                                     | Anomaly detection method introduced in Azure AI Service's [Anomaly Detector](https://learn.microsoft.com/en-us/azure/ai-services/anomaly-detector/overview)                                                                                              |
| 2019 | [dShark](https://dl.acm.org/doi/10.5555/3323234.3323252)                                                                                                                       | Diagnostic tool for capturing packet traces across data center networks                                                                                                                                                                                  |
| 2020 | [BRAIN](https://www.microsoft.com/en-us/research/publication/towards-intelligent-incident-management-why-we-need-it-and-how-we-make-it/)                                       | AIOps-centric platform for incident management                                                                                                                                                                                                           |
| 2020 | [Decaf](https://dl.acm.org/doi/abs/10.1145/3377813.3381353)                                                                                                                    | System to assist triage and initial diagnosis of incidents in Microsoft 365                                                                                                                                                                              |
| 2020 | [Gandalf](https://www.microsoft.com/en-us/research/publication/an-intelligent-end-to-end-analytics-service-for-safe-deployment-in-large-scale-cloud-infrastructure/)           | Monitoring system to early detect issues arising from deployments of fixes and updates in Azure platform to prevent impact escalation                                                                                                                    |
| 2020 | [Lumos](https://www.microsoft.com/en-us/research/publication/lumos-a-library-for-diagnosing-metric-regressions-in-web-scale-applications/)                                     | Library to reduce false positives in existing anomaly detection systems and assist in identifying root causes                                                                                                                                            |
| 2020 | [MTAD-GAT](https://ieeexplore.ieee.org/document/9338317)                                                                                                                       | Multivariate anomaly detection for time series data using graph neural networks, introduced in Azure AI Service's [Anomaly Detector](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/introducing-multivariate-anomaly-detection/2260679) |
| 2021 | [CARE](https://dl.acm.org/doi/10.1145/3447851.3458737)                                                                                                                         | Automated RCA system used in Microsoft 365 services                                                                                                                                                                                                      |
| 2022 | [MTHC](https://dl.acm.org/doi/10.1145/3534678.3539176)                                                                                                                         | Method to classify causes of disk failures used in Microsoft 365's disk failure prediction system                                                                                                                                                        |
| 2022 | [NENYA](https://www.microsoft.com/en-us/research/publication/nenya-cascade-reinforcement-learning-for-cost-aware-failure-mitigation-at-microsoft-365/)                         | Monitoring system for predictive mitigation and reinforcement learning-based policy adjustment for databases in Microsoft 365                                                                                                                            |
| 2022 | [T-SMOTE](https://www.microsoft.com/en-us/research/publication/t-smote-temporal-oriented-synthetic-minority-oversampling-technique-for-imbalanced-time-series-classification/) | Framework for training time series models aimed at early prediction of far-future anomalies, deployed in Azure and Microsoft 365                                                                                                                         |
| 2023 | [Diffusion+](https://www.microsoft.com/en-us/research/publication/diffusion-based-time-series-data-imputation-for-cloud-failure-prediction-at-microsoft-365/)                  | Method for imputing missing data for disk failure prediction in Microsoft 365                                                                                                                                                                            |
| 2023 | [EDITS](https://dl.acm.org/doi/10.1145/3543873.3584630)                                                                                                                        | Curriculum learning method for training failure prediction models, deployed in services of Azure and Microsoft 365                                                                                                                                       |
| 2023 | [HRLHF](https://dl.acm.org/doi/10.1145/3580305.3599934)                                                                                                                        | Automated RCA system introduced in Microsoft 365's Exchange services                                                                                                                                                                                     |
| 2023 | [Hyrax](https://www.microsoft.com/en-us/research/blog/a-fail-in-place-approach-for-sustainable-server-operations/)                                                             | Fail-in-place paradigm for keeping partially failed servers operational                                                                                                                                                                                  |
| 2023 | [STEAM](https://www.microsoft.com/en-us/research/publication/steam-observability-preserving-trace-sampling/)                                                                   | Tail sampling method for distributed traces using graph contrastive learning                                                                                                                                                                             |
| 2023 | [TraceDiag](https://dl.acm.org/doi/10.1145/3611643.3613864)                                                                                                                    | Automated RCA system introduced in Microsoft 365's Exchange services                                                                                                                                                                                     |
| 2023 | [iPACK](https://www.microsoft.com/en-us/research/publication/incident-aware-duplicate-ticket-aggregation-for-cloud-systems/)                                                   | Method to aggregate support tickets for the same issue based on alert information                                                                                                                                                                        |
| 2024 | [AIOpsLab](https://www.microsoft.com/en-us/research/publication/building-ai-agents-for-autonomous-clouds-challenges-and-design-principles/)                                    | Prototype implementation of an agent-based AIOps platform to streamline incident response                                                                                                                                                                |
| 2024 | [Automated Root Causing](https://dl.acm.org/doi/10.1145/3663529.3663846)                                                                                                       | Automated RCA system using context-based learning (ICL) with LLM                                                                                                                                                                                         |
| 2024 | [Early Bird](https://www.microsoft.com/en-us/research/publication/early-bird-ensuring-reliability-of-cloud-systems-through-early-failure-prediction/)                          | Framework for training time series models aimed at early prediction of far-future anomalies                                                                                                                                                              |
| 2024 | [FCVAE](https://dl.acm.org/doi/10.1145/3589334.3645710)                                                                                                                        | VAE-based network failure detection                                                                                                                                                                                                                      |
| 2024 | [FLASH](https://www.microsoft.com/en-us/research/publication/flash-a-workflow-automation-agent-for-diagnosing-recurring-incidents/)                                            | AI agent-based incident management system performing step-by-step troubleshooting                                                                                                                                                                        |
| 2024 | [ImDiffusion](https://www.microsoft.com/en-us/research/publication/imdiffusion-imputed-diffusion-models-for-multivariate-time-series-anomaly-detection/)                       | Multivariate time series anomaly detection system using time series imputation and diffusion models for Microsoft's email delivery service                                                                                                               |
| 2024 | [NetVigil](https://www.microsoft.com/en-us/research/publication/netvigil-robust-and-low-cost-anomaly-detection-for-east-west-data-center-security/)                            | Anomaly detection system for east-west data center traffic using graph neural network-based contrastive learning methods                                                                                                                                 |
| 2024 | [ReAct](https://dl.acm.org/doi/10.1145/3663529.3663841)                                                                                                                        | Prototype RCA diagnosis system using LLM-based AI agents                                                                                                                                                                                                 |
| 2024 | [SWARM](https://www.microsoft.com/en-us/research/publication/enhancing-network-failure-mitigation-with-performance-aware-ranking/)                                             | System for ranking DCN failure mitigation measures based on connection quality (CLP)                                                                                                                                                                     |

This table includes a variety of advanced, experimental, and lesser-known systems. For full details, please explore the provided links.

## References

- [Cloud Intelligence/AIOps – Infusing AI into Cloud Computing Systems - Microsoft Research](https://www.microsoft.com/en-us/research/blog/cloud-intelligence-aiops-infusing-ai-into-cloud-computing-systems/)
- [Building toward more autonomous and proactive cloud technologies with AI - Microsoft Research](https://www.microsoft.com/en-us/research/blog/building-toward-more-autonomous-and-proactive-cloud-technologies-with-ai/)
- [Automatic post-deployment management of cloud applications - Microsoft Research](https://www.microsoft.com/en-us/research/blog/automatic-post-deployment-management-of-cloud-applications/)
- [Using AI for tiered cloud platform operation - Microsoft Research](https://www.microsoft.com/en-us/research/blog/using-ai-for-tiered-cloud-platform-operation/)
- [Episode 459 - AIOps - YouTube (@The Azure Podcast)](https://www.youtube.com/watch?v=Ousa2qWQEiQ)
