# Agents Documentation

## Overview

The Rural Health Navigator uses a multi-agent architecture orchestrated by LangGraph. Each agent has a single responsibility and updates a shared state object. The Supervisor Agent coordinates execution and determines which agents should run based on user intent.

---

# 1. Supervisor Agent

## Purpose

Acts as the central orchestrator of the system.

## Responsibilities

* Analyze user request
* Create execution plan
* Route tasks to specialized agents
* Manage workflow state
* Collect agent outputs
* Determine next actions

## Inputs

* User query
* Current workflow state

## Outputs

* Execution plan
* Routing decisions

## Example

User Query:

"I have chest pain and need a clinic near me."

Supervisor Plan:

1. Run Triage Agent
2. Run Resource Finder Agent
3. Generate Care Plan
4. Run Reflection Agent

---

# 2. Triage Agent

## Purpose

Assess symptom severity and determine urgency level.

## Responsibilities

* Analyze symptoms
* Retrieve relevant medical guidance
* Classify risk level
* Recommend care urgency

## Tools

### medical_rag_search()

Retrieves information from:

* CDC documents
* NIH documents
* Medical knowledge base

### symptom_classifier()

Determines:

* Low Risk
* Medium Risk
* High Risk

## Inputs

* Symptoms
* User query

## Outputs

```json
{
  "risk_level": "HIGH",
  "recommendation": "Seek immediate medical attention"
}
```

---

# 3. Insurance Agent

## Purpose

Determine insurance coverage information.

## Responsibilities

* Analyze coverage requests
* Retrieve insurance policy information
* Check eligibility rules
* Identify prior authorization requirements

## Tools

### policy_rag_search()

Retrieves information from:

* Medicare documents
* Medicaid documents
* Insurance policy PDFs

### coverage_lookup()

Returns simulated coverage details.

## Inputs

* Insurance type
* Requested service

## Outputs

```json
{
  "covered": true,
  "prior_authorization": true,
  "notes": "MRI requires authorization"
}
```

---

# 4. Resource Finder Agent

## Purpose

Locate healthcare resources near the user.

## Responsibilities

* Search nearby clinics
* Search hospitals
* Search urgent care centers
* Rank providers by distance

## Tools

### clinic_search()

### maps_api_search()

Possible integrations:

* Google Maps API
* OpenStreetMap

## Inputs

* Location
* Care requirements

## Outputs

```json
{
  "clinics": [
    {
      "name": "Rural Health Clinic",
      "distance": "10 miles"
    }
  ]
}
```

---

# 5. Appointment Preparation Agent

## Purpose

Prepare users for healthcare visits.

## Responsibilities

* Generate visit summary
* Create symptom timeline
* Suggest questions for provider
* Organize relevant information

## Tools

### generate_visit_summary()

### generate_doctor_questions()

## Inputs

* Symptoms
* Insurance findings
* Clinic information

## Outputs

```json
{
  "visit_summary": "...",
  "questions": [
    "What may be causing my symptoms?",
    "What tests should be considered?"
  ]
}
```

---

# 6. Care Plan Agent

## Purpose

Combine outputs from all agents into a unified recommendation.

## Responsibilities

* Merge agent results
* Generate personalized care plan
* Prioritize recommendations
* Produce final guidance

## Inputs

* Triage results
* Insurance results
* Resource results
* Appointment preparation

## Outputs

```json
{
  "care_plan": "Visit Rural Health Clinic within 24 hours."
}
```

---

# 7. Reflection Agent

## Purpose

Validate the quality and completeness of the workflow.

## Responsibilities

* Verify all required tasks completed
* Detect missing information
* Recommend retries when necessary
* Improve reliability

## Validation Checks

* Was triage completed?
* Was insurance checked?
* Was a clinic found?
* Was a care plan generated?

## Inputs

* Entire workflow state

## Outputs

```json
{
  "status": "PASS",
  "missing_steps": []
}
```

or

```json
{
  "status": "FAIL",
  "missing_steps": [
    "clinic_search"
  ]
}
```

---

# Human Approval Node

## Purpose

Provide a human-in-the-loop checkpoint before final recommendations.

## Responsibilities

* Present final care plan
* Request user confirmation
* Prevent unintended actions

## Example

"Would you like to proceed with this care plan?"

User:

"Yes"

Workflow continues.

---

# Agent Communication Model

Agents do not communicate directly.

All communication occurs through the shared LangGraph state.

```text
Agent
  ↓
Update State
  ↓
Next Agent Reads State
```

This ensures predictable and auditable workflows.

---

# Future Agents

Potential future additions:

* Transportation Agent
* Medication Assistance Agent
* Telehealth Agent
* Benefits Enrollment Agent
* Appointment Scheduling Agent
* MCP Tool Discovery Agent
