"""
Prompt templates and utilities for AI capabilities in the Justice Bid system.

This module defines structured prompts for various AI functionalities, including
chat, rate recommendations, document analysis, and process management. It provides
functions to format, customize, and retrieve prompt templates with context-specific
data.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from langchain.prompts import PromptTemplate

from .models import AIUseCase
from ...utils.logging import logger

# Dictionary to store prompt templates
PROMPT_TEMPLATES: Dict[str, str] = {}

# System prompts for different AI use cases
SYSTEM_PROMPTS: Dict[AIUseCase, str] = {
    AIUseCase.CHAT: """
    You are an expert AI assistant for the Justice Bid Rate Negotiation System. 
    You help users with legal rate negotiations between law firms and their clients.
    Answer questions accurately and helpfully based on the context provided.
    If you don't know something, say so rather than making up information.
    """,
    
    AIUseCase.RATE_RECOMMENDATION: """
    You are an expert legal rate analyst for the Justice Bid Rate Negotiation System.
    Your job is to provide data-driven recommendations on rate proposals based on 
    historical data, peer comparisons, attorney performance, and client rate rules.
    Provide clear, balanced recommendations with supporting rationale.
    """,
    
    AIUseCase.DOCUMENT_ANALYSIS: """
    You are an expert legal document analyst for the Justice Bid Rate Negotiation System.
    Your job is to analyze Outside Counsel Guidelines and other legal documents,
    identifying key terms, requirements, and negotiable sections.
    Provide clear summaries and recommendations based on document content.
    """,
    
    AIUseCase.PROCESS_MANAGEMENT: """
    You are an expert workflow assistant for the Justice Bid Rate Negotiation System.
    Your job is to help users manage their rate negotiation process by prioritizing
    actions, suggesting next steps, and drafting communications.
    Provide practical, actionable guidance to improve efficiency.
    """
}

# Rate recommendation prompt template
RATE_RECOMMENDATION_PROMPT = """
You are an expert legal rate analyst helping {user_role} at {organization_name}.

Consider the following information:
- Current Rate: {current_rate}
- Proposed Rate: {proposed_rate}
- Percentage Increase: {percentage_increase}%

HISTORICAL RATES:
{historical_rates}

PEER COMPARISON:
{peer_comparison}

ATTORNEY PERFORMANCE:
{performance_metrics}

CLIENT RATE RULES:
{rate_rules}

Based on this information, provide:
1. A recommended action (approve/reject/counter) for the proposed rate
2. A specific counter-proposal value if appropriate
3. A brief explanation of your reasoning
4. Any additional factors that should be considered

Your recommendations should be data-driven, fair, and aligned with market standards.
"""

# Counter-proposal prompt template
COUNTER_PROPOSAL_PROMPT = """
You are an expert legal rate analyst helping {user_role} at {organization_name}.

Task: Recommend a fair counter-proposal rate based on the following information:

RATE INFORMATION:
- Current Rate: ${current_rate}
- Proposed Rate: ${proposed_rate}
- Proposed Increase: {percentage_increase}%

HISTORICAL CONTEXT:
{historical_data}

PEER COMPARISON:
{peer_data}

ATTORNEY PERFORMANCE:
{performance_data}

CLIENT RATE RULES:
{rate_rules}

Based on the above information, suggest a specific counter-proposal amount that:
1. Balances fair compensation with client value
2. Aligns with market rates for comparable attorneys
3. Reflects the attorney's performance
4. Complies with client rate rules

Provide the counter-proposal amount and a brief justification.
"""

# Recommendation explanation prompt template
RECOMMENDATION_EXPLANATION_PROMPT = """
You are an expert legal rate analyst helping {user_role} at {organization_name}.

RECOMMENDATION DETAILS:
{recommendation}

CONTEXTUAL FACTORS:
{context_data}

Provide a detailed explanation of the recommendation that includes:
1. The primary factors that influenced the recommendation
2. How the recommendation compares to peer benchmarks
3. How historical data informed the decision
4. Any special considerations or exceptions
5. The expected impact of this recommendation

Your explanation should be clear, thorough, and data-driven, helping the user 
understand the rationale behind the recommendation.
"""

# Chat prompt template
CHAT_PROMPT = """
You are an AI assistant for the Justice Bid Rate Negotiation System, helping {user_role} at {organization_name}.

USER CONTEXT:
{user_context}

CHAT HISTORY:
{message_history}

Respond to the user's most recent question or request in a helpful, accurate manner.
If you need more information to provide a good answer, ask clarifying questions.
If the request is outside your capabilities or knowledge, explain what you can and cannot help with.
"""

# Process management prompt template
PROCESS_MANAGEMENT_PROMPT = """
You are a workflow assistant for the Justice Bid Rate Negotiation System, helping {user_role} at {organization_name}.

PENDING ACTIONS:
{pending_actions}

USER PREFERENCES:
{user_preferences}

CONTEXTUAL INFORMATION:
{context_data}

Based on the above information, recommend the most efficient way to manage these tasks.
Provide:
1. A prioritized list of actions with reasoning
2. Suggested timeframes for completion
3. Any opportunities for batch processing or automation
4. Next steps once these actions are completed

Your recommendations should focus on efficient process management while ensuring
quality outcomes for the rate negotiation process.
"""

# Action prioritization prompt template
ACTION_PRIORITIZATION_PROMPT = """
You are a workflow assistant for the Justice Bid Rate Negotiation System, helping {user_role} at {organization_name}.

The following actions require attention:

{actions}

USER PREFERENCES:
{user_preferences}

USER CONTEXT:
{user_context}

Prioritize these actions based on:
1. Urgency (deadlines and time sensitivity)
2. Importance (impact on negotiations and relationships)
3. Dependency (actions that block other actions)
4. Efficiency (opportunities for batch processing)

For each action, provide:
1. Priority level (High/Medium/Low)
2. Recommended timeframe
3. Brief rationale for the priority assignment

Present the actions in priority order with the most important at the top.
"""

# Next steps prompt template
NEXT_STEPS_PROMPT = """
You are a workflow assistant for the Justice Bid Rate Negotiation System, helping {user_role} at {organization_name}.

CURRENT CONTEXT ({context_type}):
{context_data}

USER INFORMATION:
{user_data}

Based on the current context, recommend the most appropriate next steps.
Consider:
1. Where this falls in the typical workflow
2. Any dependencies or prerequisites
3. Time-sensitive aspects or deadlines
4. Potential obstacles or challenges

Provide a clear, sequenced list of recommended next steps with brief explanations
for each recommendation.
"""

# Message draft prompt template
MESSAGE_DRAFT_PROMPT = """
You are a communication assistant for the Justice Bid Rate Negotiation System, helping {user_role} at {organization_name}.

THREAD HISTORY:
{thread_history}

MESSAGE TYPE:
{message_type}

USER PREFERENCES:
{user_preferences}

Draft a {message_type} message that:
1. Maintains appropriate professional tone
2. Clearly communicates key points
3. Provides necessary context
4. Invites appropriate response or action
5. Aligns with the user's communication style

Keep the message concise but comprehensive, focusing on clarity and actionability.
"""


def get_prompt_template(template_name: str, template_string: str = None) -> PromptTemplate:
    """
    Retrieves a prompt template by name or creates a new one if not found.
    
    Args:
        template_name: Name of the template to retrieve
        template_string: Optional template string to use if template not found
        
    Returns:
        A LangChain prompt template object
    """
    global PROMPT_TEMPLATES
    
    # Check if template exists
    if template_name in PROMPT_TEMPLATES:
        template_string = PROMPT_TEMPLATES[template_name]
        # Parse input variables from template string
        input_variables = [v.strip('{}') for v in PromptTemplate.extract_template_variables(template_string)]
        return PromptTemplate(template=template_string, input_variables=input_variables)
    
    # If template not found but template_string provided, create a new one
    if template_string:
        # Parse input variables from template string
        input_variables = [v.strip('{}') for v in PromptTemplate.extract_template_variables(template_string)]
        template = PromptTemplate(template=template_string, input_variables=input_variables)
        # Store for future use
        PROMPT_TEMPLATES[template_name] = template_string
        return template
    
    # If template not found and no template_string provided, raise error
    raise ValueError(f"Prompt template '{template_name}' not found and no template string provided")


def create_chat_prompt(user_context: Dict[str, Any], system_context: Dict[str, Any], message_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Creates a chat prompt with system instructions, user context, and message history.
    
    Args:
        user_context: Dictionary containing user-specific context
        system_context: Dictionary containing system context
        message_history: List of previous messages in the conversation
        
    Returns:
        Formatted chat prompt with system, user context, and messages
    """
    # Get system prompt for chat
    system_prompt = SYSTEM_PROMPTS.get(AIUseCase.CHAT, "You are an AI assistant for Justice Bid.")
    
    # Format system prompt with context
    if system_context:
        system_prompt_template = PromptTemplate(template=system_prompt, input_variables=list(system_context.keys()))
        system_prompt = system_prompt_template.format(**system_context)
    
    # Format user context
    user_context_str = "\n".join([f"{key}: {value}" for key, value in user_context.items()])
    
    # Format message history
    formatted_messages = []
    for message in message_history:
        role = message.get("role", "user")
        content = message.get("content", "")
        formatted_messages.append(f"{role.upper()}: {content}")
    message_history_str = "\n".join(formatted_messages)
    
    # Create chat prompt dictionary
    chat_prompt = {
        "system": system_prompt,
        "user_context": user_context_str,
        "message_history": message_history_str,
        "messages": message_history
    }
    
    return chat_prompt


def create_rate_recommendation_prompt(
    rate_data: Dict[str, Any],
    historical_data: Dict[str, Any],
    peer_data: Dict[str, Any],
    performance_data: Dict[str, Any],
    rate_rules: Dict[str, Any]
) -> str:
    """
    Creates a prompt for generating rate recommendations based on historical and peer data.
    
    Args:
        rate_data: Current and proposed rate information
        historical_data: Historical rate data
        peer_data: Peer comparison data
        performance_data: Attorney performance data
        rate_rules: Client rate rules
        
    Returns:
        Formatted prompt for rate recommendation
    """
    # Get template
    template = get_prompt_template("rate_recommendation", RATE_RECOMMENDATION_PROMPT)
    
    # Format rate data
    current_rate = rate_data.get("current_rate", 0)
    proposed_rate = rate_data.get("proposed_rate", 0)
    
    # Calculate percentage increase
    try:
        percentage_increase = round(((proposed_rate - current_rate) / current_rate) * 100, 2) if current_rate > 0 else 0
    except (TypeError, ZeroDivisionError):
        percentage_increase = 0
        logger.warning("Error calculating percentage increase", extra={
            "additional_data": {"current_rate": current_rate, "proposed_rate": proposed_rate}
        })
    
    # Format historical rates
    historical_rates_str = "No historical data available."
    if historical_data:
        historical_rates_lines = []
        for year, rate in historical_data.get("rates", {}).items():
            historical_rates_lines.append(f"- {year}: ${rate}")
        if historical_rates_lines:
            historical_rates_str = "\n".join(historical_rates_lines)
    
    # Format peer comparison
    peer_comparison_str = "No peer comparison data available."
    if peer_data:
        peer_comparison_lines = []
        peer_avg = peer_data.get("average_rate", 0)
        peer_min = peer_data.get("min_rate", 0)
        peer_max = peer_data.get("max_rate", 0)
        peer_comparison_lines.append(f"- Peer Average Rate: ${peer_avg}")
        peer_comparison_lines.append(f"- Peer Rate Range: ${peer_min} - ${peer_max}")
        if peer_data.get("percentile"):
            peer_comparison_lines.append(f"- Proposed Rate Percentile: {peer_data['percentile']}%")
        if peer_comparison_lines:
            peer_comparison_str = "\n".join(peer_comparison_lines)
    
    # Format performance metrics
    performance_metrics_str = "No performance data available."
    if performance_data:
        performance_metrics_lines = []
        if "hours" in performance_data:
            performance_metrics_lines.append(f"- Hours (Last 12mo): {performance_data['hours']}")
        if "matters" in performance_data:
            performance_metrics_lines.append(f"- Matters: {performance_data['matters']}")
        if "rating" in performance_data:
            performance_metrics_lines.append(f"- Client Rating: {performance_data['rating']}")
        if "unicourt_percentile" in performance_data:
            performance_metrics_lines.append(f"- UniCourt Performance: {performance_data['unicourt_percentile']}th percentile")
        if performance_metrics_lines:
            performance_metrics_str = "\n".join(performance_metrics_lines)
    
    # Format rate rules
    rate_rules_str = "No specific rate rules provided."
    if rate_rules:
        rate_rules_lines = []
        if "max_increase" in rate_rules:
            rate_rules_lines.append(f"- Maximum Increase: {rate_rules['max_increase']}%")
        if "freeze_period" in rate_rules:
            rate_rules_lines.append(f"- Rate Freeze Period: {rate_rules['freeze_period']}")
        if "notice_required" in rate_rules:
            rate_rules_lines.append(f"- Notice Required: {rate_rules['notice_required']} days")
        if rate_rules_lines:
            rate_rules_str = "\n".join(rate_rules_lines)
    
    # Combine everything into prompt context
    context = {
        "user_role": rate_data.get("user_role", "legal professional"),
        "organization_name": rate_data.get("organization_name", "your organization"),
        "current_rate": current_rate,
        "proposed_rate": proposed_rate,
        "percentage_increase": percentage_increase,
        "historical_rates": historical_rates_str,
        "peer_comparison": peer_comparison_str,
        "performance_metrics": performance_metrics_str,
        "rate_rules": rate_rules_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in rate recommendation prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_counter_proposal_prompt(
    current_rate: float,
    proposed_rate: float,
    historical_data: Dict[str, Any],
    peer_data: Dict[str, Any],
    performance_data: Dict[str, Any],
    rate_rules: Dict[str, Any]
) -> str:
    """
    Creates a prompt for suggesting counter-proposal values for rates.
    
    Args:
        current_rate: Current rate amount
        proposed_rate: Proposed rate amount
        historical_data: Historical rate data
        peer_data: Peer comparison data
        performance_data: Attorney performance data
        rate_rules: Client rate rules
        
    Returns:
        Formatted prompt for counter-proposal suggestion
    """
    # Get template
    template = get_prompt_template("counter_proposal", COUNTER_PROPOSAL_PROMPT)
    
    # Calculate percentage increase
    try:
        percentage_increase = round(((proposed_rate - current_rate) / current_rate) * 100, 2) if current_rate > 0 else 0
    except (TypeError, ZeroDivisionError):
        percentage_increase = 0
        logger.warning("Error calculating percentage increase", extra={
            "additional_data": {"current_rate": current_rate, "proposed_rate": proposed_rate}
        })
    
    # Format historical data
    historical_data_str = json.dumps(historical_data, indent=2) if historical_data else "No historical data available."
    
    # Format peer data
    peer_data_str = json.dumps(peer_data, indent=2) if peer_data else "No peer comparison data available."
    
    # Format performance data
    performance_data_str = json.dumps(performance_data, indent=2) if performance_data else "No performance data available."
    
    # Format rate rules
    rate_rules_str = json.dumps(rate_rules, indent=2) if rate_rules else "No specific rate rules provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": "legal professional",
        "organization_name": "your organization",
        "current_rate": current_rate,
        "proposed_rate": proposed_rate,
        "percentage_increase": percentage_increase,
        "historical_data": historical_data_str,
        "peer_data": peer_data_str,
        "performance_data": performance_data_str,
        "rate_rules": rate_rules_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in counter proposal prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_recommendation_explanation_prompt(
    recommendation: Dict[str, Any],
    context_data: Dict[str, Any]
) -> str:
    """
    Creates a prompt for generating detailed explanations of rate recommendations.
    
    Args:
        recommendation: Recommendation details
        context_data: Additional context for the explanation
        
    Returns:
        Formatted prompt for recommendation explanation
    """
    # Get template
    template = get_prompt_template("recommendation_explanation", RECOMMENDATION_EXPLANATION_PROMPT)
    
    # Format recommendation details
    recommendation_str = json.dumps(recommendation, indent=2) if recommendation else "No recommendation provided."
    
    # Format context data
    context_data_str = json.dumps(context_data, indent=2) if context_data else "No additional context provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": context_data.get("user_role", "legal professional"),
        "organization_name": context_data.get("organization_name", "your organization"),
        "recommendation": recommendation_str,
        "context_data": context_data_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in recommendation explanation prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_process_management_prompt(
    pending_actions: List[Dict[str, Any]],
    user_preferences: Dict[str, Any],
    context_data: Dict[str, Any]
) -> str:
    """
    Creates a prompt for AI-driven process management suggestions.
    
    Args:
        pending_actions: List of actions requiring attention
        user_preferences: User preferences for process management
        context_data: Additional context information
        
    Returns:
        Formatted prompt for process management
    """
    # Get template
    template = get_prompt_template("process_management", PROCESS_MANAGEMENT_PROMPT)
    
    # Format pending actions
    pending_actions_str = "No pending actions."
    if pending_actions:
        pending_actions_lines = []
        for i, action in enumerate(pending_actions, 1):
            action_type = action.get("type", "Action")
            description = action.get("description", "No description")
            deadline = action.get("deadline", "No deadline")
            pending_actions_lines.append(f"{i}. {action_type}: {description} (Deadline: {deadline})")
            if "related_to" in action:
                pending_actions_lines.append(f"   Related to: {action['related_to']}")
        pending_actions_str = "\n".join(pending_actions_lines)
    
    # Format user preferences
    user_preferences_str = json.dumps(user_preferences, indent=2) if user_preferences else "No specific preferences provided."
    
    # Format context data
    context_data_str = json.dumps(context_data, indent=2) if context_data else "No additional context provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": context_data.get("user_role", "legal professional"),
        "organization_name": context_data.get("organization_name", "your organization"),
        "pending_actions": pending_actions_str,
        "user_preferences": user_preferences_str,
        "context_data": context_data_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in process management prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_action_prioritization_prompt(
    actions: List[Dict[str, Any]],
    user_preferences: Dict[str, Any],
    user_context: Dict[str, Any]
) -> str:
    """
    Creates a prompt for prioritizing user actions based on urgency and importance.
    
    Args:
        actions: List of actions to prioritize
        user_preferences: User preferences for prioritization
        user_context: Additional user context
        
    Returns:
        Formatted prompt for action prioritization
    """
    # Get template
    template = get_prompt_template("action_prioritization", ACTION_PRIORITIZATION_PROMPT)
    
    # Format actions
    actions_str = "No actions to prioritize."
    if actions:
        actions_lines = []
        for i, action in enumerate(actions, 1):
            action_type = action.get("type", "Action")
            description = action.get("description", "No description")
            deadline = action.get("deadline", "No deadline")
            importance = action.get("importance", "Medium")
            actions_lines.append(f"{i}. {action_type}: {description}")
            actions_lines.append(f"   Deadline: {deadline}")
            actions_lines.append(f"   Importance: {importance}")
            if "dependencies" in action:
                actions_lines.append(f"   Dependencies: {', '.join(action['dependencies'])}")
            actions_lines.append("")  # Empty line for readability
        actions_str = "\n".join(actions_lines)
    
    # Format user preferences
    user_preferences_str = json.dumps(user_preferences, indent=2) if user_preferences else "No specific preferences provided."
    
    # Format user context
    user_context_str = json.dumps(user_context, indent=2) if user_context else "No additional context provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": user_context.get("user_role", "legal professional"),
        "organization_name": user_context.get("organization_name", "your organization"),
        "actions": actions_str,
        "user_preferences": user_preferences_str,
        "user_context": user_context_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in action prioritization prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_next_steps_prompt(
    context_type: str,
    context_data: Dict[str, Any],
    user_data: Dict[str, Any]
) -> str:
    """
    Creates a prompt for suggesting next steps based on context.
    
    Args:
        context_type: Type of context (e.g., "negotiation", "rate submission")
        context_data: Context-specific data
        user_data: User-specific data
        
    Returns:
        Formatted prompt for next steps suggestion
    """
    # Get template
    template = get_prompt_template("next_steps", NEXT_STEPS_PROMPT)
    
    # Format context data
    context_data_str = json.dumps(context_data, indent=2) if context_data else "No context data provided."
    
    # Format user data
    user_data_str = json.dumps(user_data, indent=2) if user_data else "No user data provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": user_data.get("user_role", "legal professional"),
        "organization_name": user_data.get("organization_name", "your organization"),
        "context_type": context_type,
        "context_data": context_data_str,
        "user_data": user_data_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in next steps prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def create_message_draft_prompt(
    thread_history: List[Dict[str, str]],
    message_type: str,
    user_preferences: Dict[str, Any]
) -> str:
    """
    Creates a prompt for drafting follow-up messages based on thread history.
    
    Args:
        thread_history: Previous messages in the thread
        message_type: Type of message to draft (e.g., "follow-up", "counter-proposal")
        user_preferences: User preferences for message style
        
    Returns:
        Formatted prompt for message drafting
    """
    # Get template
    template = get_prompt_template("message_draft", MESSAGE_DRAFT_PROMPT)
    
    # Format thread history
    thread_history_str = "No thread history."
    if thread_history:
        thread_history_lines = []
        for message in thread_history:
            sender = message.get("sender", "Unknown")
            content = message.get("content", "No content")
            timestamp = message.get("timestamp", "No timestamp")
            thread_history_lines.append(f"FROM: {sender}")
            thread_history_lines.append(f"TIME: {timestamp}")
            thread_history_lines.append(f"MESSAGE: {content}")
            thread_history_lines.append("")  # Empty line for readability
        thread_history_str = "\n".join(thread_history_lines)
    
    # Format user preferences
    user_preferences_str = json.dumps(user_preferences, indent=2) if user_preferences else "No specific preferences provided."
    
    # Combine everything into prompt context
    context = {
        "user_role": user_preferences.get("user_role", "legal professional"),
        "organization_name": user_preferences.get("organization_name", "your organization"),
        "thread_history": thread_history_str,
        "message_type": message_type,
        "user_preferences": user_preferences_str
    }
    
    # Format template with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in message draft prompt: {str(e)}", extra={
            "additional_data": {"context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


def load_prompt_templates() -> None:
    """
    Loads prompt templates from configured sources (files or environment).
    """
    global PROMPT_TEMPLATES
    
    # Check for environment variable with template path
    template_path = os.environ.get("PROMPT_TEMPLATES_PATH")
    
    if template_path and os.path.exists(template_path):
        logger.info(f"Loading prompt templates from {template_path}")
        
        # If it's a directory, load all JSON files
        if os.path.isdir(template_path):
            for filename in os.listdir(template_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(template_path, filename)
                    try:
                        with open(file_path, "r") as f:
                            templates = json.load(f)
                            for name, template in templates.items():
                                PROMPT_TEMPLATES[name] = template
                                logger.debug(f"Loaded template: {name}")
                    except Exception as e:
                        logger.error(f"Error loading template file {filename}: {str(e)}")
        
        # If it's a file, load it directly
        elif os.path.isfile(template_path) and template_path.endswith(".json"):
            try:
                with open(template_path, "r") as f:
                    templates = json.load(f)
                    for name, template in templates.items():
                        PROMPT_TEMPLATES[name] = template
                        logger.debug(f"Loaded template: {name}")
            except Exception as e:
                logger.error(f"Error loading template file {template_path}: {str(e)}")
    else:
        # Use built-in templates
        PROMPT_TEMPLATES = {
            "rate_recommendation": RATE_RECOMMENDATION_PROMPT,
            "counter_proposal": COUNTER_PROPOSAL_PROMPT,
            "recommendation_explanation": RECOMMENDATION_EXPLANATION_PROMPT,
            "chat": CHAT_PROMPT,
            "process_management": PROCESS_MANAGEMENT_PROMPT,
            "action_prioritization": ACTION_PRIORITIZATION_PROMPT,
            "next_steps": NEXT_STEPS_PROMPT,
            "message_draft": MESSAGE_DRAFT_PROMPT
        }
        logger.info("Using built-in prompt templates")
    
    # Log number of loaded templates
    logger.info(f"Loaded {len(PROMPT_TEMPLATES)} prompt templates")


def format_prompt_with_context(template_name: str, context: Dict[str, Any]) -> str:
    """
    Formats a prompt template with provided context variables.
    
    Args:
        template_name: Name of the template to format
        context: Context variables for formatting
        
    Returns:
        Formatted prompt string
    """
    # Get template
    template = get_prompt_template(template_name)
    
    # Format with context
    try:
        return template.format(**context)
    except KeyError as e:
        logger.error(f"Missing key in prompt template: {str(e)}", extra={
            "additional_data": {"template_name": template_name, "context_keys": list(context.keys())}
        })
        # Add missing keys with placeholder values
        for key in template.input_variables:
            if key not in context:
                context[key] = f"[No data for {key}]"
        return template.format(**context)


class PromptManager:
    """
    Manages prompt templates and their creation across AI capabilities.
    
    This class provides a centralized way to manage prompt templates,
    register new templates, and format prompts with context variables.
    """
    
    def __init__(self):
        """Initialize the prompt manager with default templates."""
        # Initialize template dictionaries
        self._templates = {}
        self._system_prompts = {}
        
        # Load default templates
        for name, template in PROMPT_TEMPLATES.items():
            self.register_template(name, template)
        
        # Register system prompts
        for use_case, prompt in SYSTEM_PROMPTS.items():
            self._system_prompts[use_case] = prompt
    
    def get_template(self, template_name: str) -> PromptTemplate:
        """
        Retrieves a prompt template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            The requested prompt template
            
        Raises:
            KeyError: If template not found
        """
        if template_name in self._templates:
            return self._templates[template_name]
        
        raise KeyError(f"Template '{template_name}' not found. Available templates: {list(self._templates.keys())}")
    
    def register_template(self, template_name: str, template_string: str) -> PromptTemplate:
        """
        Registers a new prompt template.
        
        Args:
            template_name: Name for the template
            template_string: Template string
            
        Returns:
            The newly created prompt template
        """
        # Extract input variables from template string
        input_variables = [v.strip('{}') for v in PromptTemplate.extract_template_variables(template_string)]
        
        # Create template
        template = PromptTemplate(template=template_string, input_variables=input_variables)
        
        # Store template
        self._templates[template_name] = template
        
        logger.debug(f"Registered template: {template_name}")
        return template
    
    def get_system_prompt(self, use_case: AIUseCase) -> str:
        """
        Gets the system prompt for a specific AI use case.
        
        Args:
            use_case: The AI use case
            
        Returns:
            System prompt for the specified use case
        """
        if use_case in self._system_prompts:
            return self._system_prompts[use_case]
        
        # Return default if not found
        logger.warning(f"No system prompt defined for use case {use_case.value}, using default")
        return self._system_prompts.get(AIUseCase.CHAT, "You are an AI assistant for Justice Bid.")
    
    def format_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Formats a prompt template with context variables.
        
        Args:
            template_name: Name of the template to format
            context: Context variables for formatting
            
        Returns:
            Formatted prompt string
        """
        template = self.get_template(template_name)
        
        # Format with context
        try:
            return template.format(**context)
        except KeyError as e:
            logger.error(f"Missing key in prompt template: {str(e)}", extra={
                "additional_data": {"template_name": template_name, "context_keys": list(context.keys())}
            })
            # Add missing keys with placeholder values
            for key in template.input_variables:
                if key not in context:
                    context[key] = f"[No data for {key}]"
            return template.format(**context)
    
    def load_templates_from_directory(self, directory_path: str) -> int:
        """
        Loads templates from JSON files in a directory.
        
        Args:
            directory_path: Path to directory containing template files
            
        Returns:
            Number of templates loaded
        """
        count = 0
        
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            logger.error(f"Template directory not found: {directory_path}")
            return count
        
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                try:
                    with open(file_path, "r") as f:
                        templates = json.load(f)
                        for name, template in templates.items():
                            self.register_template(name, template)
                            count += 1
                except Exception as e:
                    logger.error(f"Error loading template file {filename}: {str(e)}")
        
        logger.info(f"Loaded {count} templates from {directory_path}")
        return count


# Load templates on module import
load_prompt_templates()