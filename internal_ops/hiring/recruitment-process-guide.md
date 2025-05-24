# Recruitment Process Guide

## Overview
This guide outlines the complete recruitment process using the REC Jira project to track candidates from application to onboarding.

## 🎯 Recruitment Workflow Stages

### 1. **Applications** (Initial Stage)
**Status:** `Applications`  
**Purpose:** New candidates enter the pipeline

#### Actions to Take:
- [ ] Create candidate issue in REC project
- [ ] Add relevant labels (role, department, skills)
- [ ] Review application materials (resume, portfolio, cover letter)
- [ ] Initial qualification check
- [ ] Schedule initial screening if qualified

#### Issue Creation Template:
```
Project: REC
Issue Type: Candidate
Summary: [Name] - [Position]
Labels: [role-specific], [department], [skill-tags]
```

#### Required Information:
- Full name
- Position applied for
- Contact information
- Application date
- Resume/portfolio links
- Initial qualification notes

---

### 2. **Screening** (Initial Assessment)
**Status:** `Screening`  
**Purpose:** Basic qualification and fit assessment

#### Actions to Take:
- [ ] Conduct phone/video screening (15-30 minutes)
- [ ] Verify basic qualifications
- [ ] Assess communication skills
- [ ] Gauge interest level and availability
- [ ] Check salary expectations (if applicable)
- [ ] Take screening notes in Jira comments

#### Key Screening Questions:
1. Tell me about your background and experience
2. Why are you interested in this role?
3. What are your availability and start date preferences?
4. Salary expectations (if relevant)
5. Any questions about the company/role?

#### Decision Points:
- **PASS:** Move to `Interviewing`
- **FAIL:** Move to `Rejected` with reason
- **MAYBE:** Schedule follow-up screening

---

### 3. **Interviewing** (Formal Interview Process)
**Status:** `Interviewing`  
**Purpose:** Deep dive into skills, experience, and cultural fit

#### Actions to Take:
- [ ] Schedule formal interview (45-60 minutes)
- [ ] Send calendar invite with meeting details
- [ ] Prepare role-specific interview questions
- [ ] Conduct structured interview
- [ ] Take detailed interview notes
- [ ] Assess technical skills (if applicable)
- [ ] Evaluate cultural fit

#### Interview Structure:
1. **Introduction** (5 mins): Welcome, agenda, company overview
2. **Experience Review** (15 mins): Deep dive into relevant experience
3. **Technical Assessment** (15 mins): Role-specific skills evaluation
4. **Cultural Fit** (10 mins): Values alignment, work style
5. **Questions & Next Steps** (10 mins): Candidate questions, timeline

#### Post-Interview Actions:
- [ ] Add comprehensive interview notes to Jira
- [ ] Score candidate on key criteria (1-5 scale)
- [ ] Check references if strong candidate
- [ ] Make go/no-go decision

---

### 4. **Testing** (Interview Debrief)
**Status:** `Testing`  
**Purpose:** Final evaluation and decision making

#### Actions to Take:
- [ ] Compile all evaluation data
- [ ] Review with hiring team/stakeholders
- [ ] Make final hire/no-hire decision
- [ ] Document decision rationale
- [ ] Prepare offer details (if hire decision)

#### Decision Criteria:
- Technical skills match
- Experience relevance
- Cultural fit score
- Communication skills
- Growth potential
- Reference check results

#### Decision Outcomes:
- **HIRE:** Move to `Offer Extended`
- **NO HIRE:** Move to `Rejected` with feedback
- **MAYBE:** Schedule additional interview/assessment

---

### 5. **Offer Extended** (Offer Management)
**Status:** `Offer Extended`  
**Purpose:** Managing the offer process

#### Actions to Take:
- [ ] Prepare formal offer letter
- [ ] Send offer via email
- [ ] Set acceptance deadline
- [ ] Follow up as needed
- [ ] Track offer status

#### Offer Components:
- Position title and responsibilities
- Compensation details
- Start date
- Benefits overview
- Acceptance deadline
- Next steps

---

### 6. **Hired** (Successful Completion)
**Status:** `Hired`  
**Purpose:** Candidate accepted offer and is joining

#### Actions to Take:
- [ ] Confirm start date
- [ ] Begin onboarding preparation
- [ ] Set up accounts and access
- [ ] Prepare workspace/equipment
- [ ] Schedule orientation
- [ ] Add to team communications

---

### 7. **Rejected** (Process Ended)
**Status:** `Rejected`  
**Purpose:** Candidate not selected

#### Actions to Take:
- [ ] Send professional rejection email
- [ ] Provide constructive feedback (if requested)
- [ ] Document rejection reason
- [ ] Keep in talent pool for future opportunities

---

## 🛠️ Tools and Integrations

### Jira Management
- **Create Issues:** Use `Candidate` issue type
- **Transitions:** Move through workflow stages
- **Comments:** Add detailed notes at each stage
- **Labels:** Tag with skills, roles, departments
- **Attachments:** Store resumes, portfolios

### Email Integration
- Use Gmail MCP to search for candidate emails
- Send calendar invites for interviews
- Automate follow-up communications
- Track email threads with candidates

### Calendar Management
- Schedule interviews using calendar integration
- Block time for screening calls
- Set reminders for follow-ups
- Coordinate with team calendars

## 📋 Best Practices

### Documentation Standards
1. **Always comment** when transitioning issue status
2. **Include specific feedback** in rejection decisions
3. **Track timeline** from application to decision
4. **Score consistently** using defined criteria
5. **Reference check** before final offers

### Communication Guidelines
- Respond to applications within 48 hours
- Provide clear timeline expectations
- Send professional communications
- Give constructive feedback when possible
- Keep candidates informed of status

### Efficiency Tips
- Batch similar activities (all screenings on one day)
- Use templates for common communications
- Standardize interview questions by role
- Automate calendar scheduling when possible
- Set up email filters for applications

## 🚀 Onboarding Process

### Pre-Start Checklist
- [ ] Create accounts (Slack, Jira, GitHub, Google Workspace)
- [ ] Prepare equipment and workspace
- [ ] Set up payroll information
- [ ] Send welcome package
- [ ] Schedule first day agenda

### Week 1 Agenda
- [ ] Company orientation
- [ ] Team introductions
- [ ] Role-specific training
- [ ] Tool access verification
- [ ] Initial project assignments

### Follow-up Schedule
- [ ] 1-week check-in
- [ ] 30-day review
- [ ] 90-day evaluation
- [ ] Ongoing development planning

## 📊 Metrics to Track

### Process Efficiency
- Time from application to decision
- Interview-to-hire ratio
- Candidate satisfaction scores
- Recruiter time spent per hire

### Quality Indicators
- New hire performance ratings
- 90-day retention rate
- Cultural fit assessments
- Reference check scores

## 🔄 Continuous Improvement

### Regular Reviews
- Monthly process evaluation
- Candidate feedback collection
- Interview question effectiveness
- Timeline optimization opportunities

### Process Updates
- Update this guide quarterly
- Incorporate team feedback
- Adapt to changing needs
- Share best practices across team

---

## Quick Reference Commands

### Creating New Candidate
```
Project: REC
Issue Type: Candidate
Summary: [Full Name] - [Position Title]
Description: [Use template above]
Labels: [role], [department], [skills]
```

### Common Transitions
- Applications → Screening
- Screening → Interviewing  
- Interviewing → Testing
- Testing → Offer Extended
- Offer Extended → Hired
- Any Stage → Rejected

### Email Templates Available
- Initial acknowledgment
- Screening invitation
- Interview scheduling
- Offer letter
- Rejection notice
- Onboarding welcome 