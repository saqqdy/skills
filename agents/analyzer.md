# Post-hoc Analyzer Agent

Analyze comparison results to understand WHY the winner won and generate improvement suggestions.

## Role

After comparison determines a winner, the Analyzer examines the skills and transcripts to extract actionable insights.

## Inputs

You receive:
- **winner**: "A" or "B" (from comparison)
- **winner_skill_path**: Path to the winning skill
- **winner_transcript_path**: Path to winner's transcript
- **loser_skill_path**: Path to the losing skill
- **loser_transcript_path**: Path to loser's transcript
- **comparison_result_path**: Path to comparison JSON
- **output_path**: Where to save the analysis

## Process

### Step 1: Read Comparison Result
1. Read the comparison output
2. Note the winning side and reasoning

### Step 2: Read Both Skills
1. Read winner's SKILL.md
2. Read loser's SKILL.md
3. Identify structural differences

### Step 3: Read Both Transcripts
1. Read winner's transcript
2. Read loser's transcript
3. Compare execution patterns

### Step 4: Analyze Instruction Following
Evaluate how closely each followed their skill's instructions.

### Step 5: Identify Strengths and Weaknesses
- What made the winner better?
- What held the loser back?

### Step 6: Generate Improvement Suggestions
Produce actionable suggestions for improving the loser skill.

## Output Format

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill"
  },
  "winner_strengths": [
    "Clear step-by-step instructions",
    "Included validation script",
    "Explicit error handling guidance"
  ],
  "loser_weaknesses": [
    "Vague instructions led to inconsistent behavior",
    "No validation tools",
    "Missing error handling"
  ],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace vague instructions with explicit steps",
      "expected_impact": "Would eliminate ambiguity"
    }
  ]
}
```

## Guidelines

- Be specific: Quote from skills and transcripts
- Be actionable: Provide concrete changes
- Focus on skill improvements
- Prioritize by impact
