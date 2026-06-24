# Tools Documentation

# Overview

The Rural Health Navigator uses a collection of tools that can be invoked by specialized agents through LangGraph.

Tools provide access to:

* Retrieval-Augmented Generation (RAG)
* External APIs
* Databases
* Knowledge Bases
* Utility Functions

Agents do not directly communicate with external systems. All external interactions occur through tools.

---

# Tool Architecture

```text
Agent
  ↓
Tool Call
  ↓
External System / Database
  ↓
Tool Response
  ↓
Agent Reasoning
```

---

# Triage Agent Tools

## medical_rag_search()

### Purpose

Retrieve medical guidance relevant to user symptoms.

### Data Sources

* CDC Documents
* NIH Documents
* MedlinePlus
* Rural Healthcare Resources

### Input

```json
{
  "query": "chest pain and dizziness"
}
```

### Output

```json
{
  "documents": [
    {
      "source": "CDC",
      "content": "Chest pain may require immediate medical attention..."
    }
  ]
}
```

### Implementation Type

RAG Tool

---

## symptom_classifier()

### Purpose

Determine urgency level based on symptoms.

### Input

```json
{
  "symptoms": "chest pain"
}
```

### Output

```json
{
  "risk_level": "HIGH"
}
```

### Implementation Type

LLM Tool

---

# Insurance Agent Tools

## policy_rag_search()

### Purpose

Search insurance policy documents.

### Data Sources

* Medicare PDFs
* Medicaid PDFs
* Insurance Policy Documents

### Input

```json
{
  "query": "MRI coverage"
}
```

### Output

```json
{
  "coverage_information": "MRI is covered with prior authorization."
}
```

### Implementation Type

RAG Tool

---

## coverage_lookup()

### Purpose

Provide structured coverage information.

### Input

```json
{
  "insurance": "Medicare",
  "service": "MRI"
}
```

### Output

```json
{
  "covered": true,
  "prior_authorization": true
}
```

### Implementation Type

Mock Tool (MVP)

---

# Resource Finder Agent Tools

## clinic_search()

### Purpose

Locate nearby healthcare facilities.

### Input

```json
{
  "location": "Raleigh, NC"
}
```

### Output

```json
{
  "clinics": [
    {
      "name": "Rural Health Center",
      "distance": "12 miles"
    }
  ]
}
```

### Implementation Type

Maps API

---

## hospital_search()

### Purpose

Find nearby hospitals.

### Input

```json
{
  "location": "Raleigh, NC"
}
```

### Output

```json
{
  "hospitals": [
    {
      "name": "County Hospital"
    }
  ]
}
```

### Implementation Type

Maps API

---

## geolocation_lookup()

### Purpose

Convert user location into searchable coordinates.

### Input

```json
{
  "zip_code": "27529"
}
```

### Output

```json
{
  "latitude": 35.507,
  "longitude": -78.739
}
```

### Implementation Type

Utility Tool

---

# Appointment Preparation Agent Tools

## generate_visit_summary()

### Purpose

Generate a structured summary for healthcare visits.

### Input

```json
{
  "symptoms": "...",
  "duration": "2 weeks"
}
```

### Output

```json
{
  "visit_summary": "Patient reports headaches for two weeks."
}
```

### Implementation Type

LLM Tool

---

## generate_provider_questions()

### Purpose

Create suggested questions for healthcare providers.

### Input

```json
{
  "symptoms": "headache"
}
```

### Output

```json
{
  "questions": [
    "What could be causing my symptoms?",
    "Do I need additional testing?"
  ]
}
```

### Implementation Type

LLM Tool

---

# Care Plan Agent Tools

## generate_care_plan()

### Purpose

Combine outputs from multiple agents into a single recommendation.

### Input

```json
{
  "triage_result": {},
  "insurance_result": {},
  "resource_result": {}
}
```

### Output

```json
{
  "care_plan": "Visit Rural Health Center within 24 hours."
}
```

### Implementation Type

LLM Tool

---

# Reflection Agent Tools

## validate_workflow()

### Purpose

Ensure all required steps were completed.

### Validation Checks

* Triage completed
* Insurance reviewed
* Clinic identified
* Care plan generated

### Input

```json
{
  "workflow_state": {}
}
```

### Output

```json
{
  "status": "PASS"
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

### Implementation Type

Validation Tool

---

# Human Approval Tools

## request_user_confirmation()

### Purpose

Obtain user approval before final recommendations.

### Input

```json
{
  "care_plan": "Visit clinic tomorrow."
}
```

### Output

```json
{
  "approved": true
}
```

### Implementation Type

Human-in-the-Loop

---

# Future MCP-Compatible Tools

The following tools may later be exposed through MCP servers.

## Medical MCP Server

Tools:

* search_medical_guidelines()
* retrieve_condition_information()

---

## Insurance MCP Server

Tools:

* check_coverage()
* estimate_cost()

---

## Maps MCP Server

Tools:

* search_clinics()
* get_directions()

---

## Scheduling MCP Server

Tools:

* find_available_slots()
* create_appointment()

---

## Memory MCP Server

Tools:

* save_user_preference()
* retrieve_user_history()

---

# MVP Tool Classification

## Real Tools

* medical_rag_search()
* policy_rag_search()
* clinic_search()
* hospital_search()
* geolocation_lookup()

## Simulated Tools

* coverage_lookup()
* create_appointment()
* estimate_cost()

## LLM Tools

* symptom_classifier()
* generate_visit_summary()
* generate_provider_questions()
* generate_care_plan()

## Validation Tools

* validate_workflow()
* request_user_confirmation()
