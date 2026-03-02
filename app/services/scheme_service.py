"""
Government Scheme Search and Recommendation Service.
Simplified for fast performance - no LLM calls, direct RAG queries only.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.services.rag_engine import rag_engine
from app.services.translation import translation_service
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class UserProfile:
    """User profile for scheme eligibility assessment."""

    user_id: str
    location: Optional[Dict[str, Any]] = None  # {district, state, latitude, longitude}
    crops: Optional[List[str]] = None
    land_size_hectares: Optional[float] = None
    farmer_category: Optional[str] = None  # small, marginal, medium, large
    annual_income: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    caste_category: Optional[str] = None  # general, obc, sc, st
    has_bank_account: bool = True
    has_aadhaar: bool = True
    language: Optional[str] = "en"  # User's preferred language
    additional_attributes: Optional[Dict[str, Any]] = None


@dataclass
class SchemeRecommendation:
    """Scheme recommendation with eligibility and application details."""

    scheme_id: str
    scheme_name: str
    scheme_type: str
    description: str
    eligibility_score: float  # 0.0 to 1.0
    is_eligible: bool
    eligibility_reasons: List[str]
    ineligibility_reasons: List[str]
    benefits: List[str]
    application_procedure: str
    required_documents: List[str]
    application_deadline: Optional[str] = None
    contact_information: Optional[str] = None
    source_document: str = ""
    location_specific: bool = False
    priority_score: float = 0.0  # Combined score for ranking


class SchemeService:
    """Service for government scheme search and personalized recommendations."""

    def __init__(self):
        """Initialize the scheme service."""
        self.rag_engine = rag_engine

    async def get_schemes_for_user(
        self,
        user_profile: UserProfile,
        limit: int = 20,
    ) -> List[SchemeRecommendation]:
        """
        Get schemes for user based on their profile (state + central schemes).
        This is the main method for auto-loading schemes on page load.

        Args:
            user_profile: User profile with state and other details
            limit: Maximum number of schemes to return

        Returns:
            List of schemes relevant to user's state + central schemes (translated to user's language)
        """
        try:
            logger.info(f"Getting schemes for user: {user_profile.user_id}")

            # Build query from user profile
            query_parts = []

            # Add state to query if available
            if user_profile.location and user_profile.location.get("state"):
                state = user_profile.location["state"]
                query_parts.append(f"{state} schemes")

            # Add farmer type
            if user_profile.farmer_category:
                query_parts.append(f"{user_profile.farmer_category} farmer")

            # Add crops
            if user_profile.crops:
                query_parts.append(f"{', '.join(user_profile.crops[:2])}")

            # Default query
            if not query_parts:
                query_parts.append("government schemes for farmers")

            query = " ".join(query_parts)

            # Use RAG to retrieve schemes
            try:
                scheme_documents = self.rag_engine.retrieve_documents(
                    query=query,
                    collections=["government_schemes"],
                    top_k=limit * 2,  # Retrieve more for filtering
                    filters=None,
                )
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")
                # Return empty list if RAG fails (e.g., no data in vector DB)
                return []

            if not scheme_documents:
                logger.warning(f"No schemes found for user")
                return []

            # Process schemes
            recommendations = []
            for doc in scheme_documents:
                try:
                    recommendation = self._process_scheme_document(doc, user_profile)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.warning(f"Failed to process scheme document: {e}")
                    continue

            # Filter by state
            filtered = self._filter_by_state(recommendations, user_profile)

            # Sort by priority
            filtered.sort(key=lambda x: x.priority_score, reverse=True)

            result = filtered[:limit]

            # Translate schemes if user language is not English
            if user_profile.language and user_profile.language != "en":
                try:
                    result = await self._translate_schemes(
                        result, user_profile.language
                    )
                except Exception as e:
                    logger.warning(
                        f"Translation failed, returning English schemes: {e}"
                    )
                    # Continue with English schemes if translation fails

            logger.info(f"Found {len(result)} schemes for user")
            return result

        except Exception as e:
            logger.error(f"Failed to get schemes for user: {e}", exc_info=True)
            # Return empty list instead of raising to prevent 500 errors
            return []

    def prepare_chat_context(self, scheme: SchemeRecommendation) -> Dict[str, str]:
        """
        Prepare scheme context for chat integration.

        Args:
            scheme: Scheme recommendation object

        Returns:
            Dictionary with context and initial_message
        """
        try:
            # Format benefits
            benefits_text = "\n".join(f"- {b}" for b in scheme.benefits)

            # Format eligibility
            eligibility_text = (
                "\n".join(f"- {e}" for e in scheme.eligibility_reasons)
                if scheme.eligibility_reasons
                else "See scheme details"
            )

            # Format application procedure
            app_procedure = scheme.application_procedure

            # Format required documents
            docs_text = "\n".join(f"- {d}" for d in scheme.required_documents)

            # Determine eligibility status
            eligibility_status = (
                "✓ Eligible" if scheme.is_eligible else "May not be eligible"
            )
            eligibility_score_pct = f"{scheme.eligibility_score:.0%}"

            # Build context
            context = f"""User is asking about the government scheme: {scheme.scheme_name}

Scheme Type: {scheme.scheme_type}

Description:
{scheme.description}

Benefits:
{benefits_text}

Eligibility:
{eligibility_text}

Application Process:
{app_procedure}

Required Documents:
{docs_text}

User's Eligibility Status: {eligibility_status}
Eligibility Score: {eligibility_score_pct}

Please help the user understand this scheme, answer their questions about eligibility, benefits, application process, and required documents. Be helpful and provide clear, actionable information."""

            initial_message = f"I want to know more about {scheme.scheme_name}"

            return {
                "context": context,
                "initial_message": initial_message,
                "scheme_id": scheme.scheme_id,
                "scheme_name": scheme.scheme_name,
            }

        except Exception as e:
            logger.error(f"Failed to prepare chat context: {e}")
            return {
                "context": f"User is asking about {scheme.scheme_name}",
                "initial_message": f"Tell me about {scheme.scheme_name}",
                "scheme_id": scheme.scheme_id,
                "scheme_name": scheme.scheme_name,
            }

    async def search_schemes(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        top_k: int = 10,
    ) -> List[SchemeRecommendation]:
        """
        Search for government schemes with optional user profile for personalization.

        Args:
            query: Search query describing scheme needs
            user_profile: User profile for eligibility filtering
            top_k: Number of schemes to return

        Returns:
            List of scheme recommendations sorted by relevance
        """
        try:
            logger.info(f"Searching schemes for query: {query[:50]}...")

            # Retrieve relevant scheme documents using RAG
            try:
                scheme_documents = self.rag_engine.retrieve_documents(
                    query=query,
                    collections=["government_schemes"],
                    top_k=top_k * 2,  # Retrieve more for filtering
                    filters=None,
                )
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")
                # Return empty list if RAG fails
                return []

            if not scheme_documents:
                logger.warning(f"No schemes found for query: {query}")
                return []

            # Process schemes
            recommendations = []
            for doc in scheme_documents:
                try:
                    recommendation = self._process_scheme_document(doc, user_profile)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.warning(f"Failed to process scheme document: {e}")
                    continue

            # Filter by state if user profile provided
            if user_profile:
                recommendations = self._filter_by_state(recommendations, user_profile)

            # Sort by priority score
            recommendations.sort(key=lambda x: x.priority_score, reverse=True)

            # Return top k recommendations
            result = recommendations[:top_k]
            logger.info(f"Found {len(result)} scheme recommendations")
            return result

        except Exception as e:
            logger.error(f"Failed to search schemes: {e}", exc_info=True)
            # Return empty list instead of raising
            return []

    async def get_scheme_details(
        self,
        scheme_name: str,
        user_profile: Optional[UserProfile] = None,
    ) -> Optional[SchemeRecommendation]:
        """
        Get detailed information about a specific scheme.

        Args:
            scheme_name: Name of the scheme
            user_profile: Optional user profile for eligibility check

        Returns:
            Detailed scheme recommendation or None if not found
        """
        try:
            logger.info(f"Getting details for scheme: {scheme_name}")

            # Search for specific scheme
            scheme_documents = self.rag_engine.retrieve_documents(
                query=scheme_name,
                collections=["government_schemes"],
                top_k=5,
                filters=None,
            )

            if not scheme_documents:
                logger.warning(f"Scheme not found: {scheme_name}")
                return None

            # Find exact match by name
            for doc in scheme_documents:
                metadata = doc.get("metadata", {})
                doc_scheme_name = metadata.get("scheme_name", "")
                if doc_scheme_name.lower() == scheme_name.lower():
                    return self._process_scheme_document(doc, user_profile)

            # If no exact match, return first result
            return self._process_scheme_document(scheme_documents[0], user_profile)

        except Exception as e:
            logger.error(f"Failed to get scheme details: {e}")
            raise

    def _process_scheme_document(
        self,
        document: Dict[str, Any],
        user_profile: Optional[UserProfile],
    ) -> Optional[SchemeRecommendation]:
        """Process a scheme document and create recommendation."""
        try:
            content = document.get("content", "")
            metadata = document.get("metadata", {})
            similarity_score = document.get("similarity_score", 0.0)

            # Extract scheme information from structured content
            scheme_info = self._parse_scheme_content(content, metadata)

            # Calculate eligibility if user profile provided
            if user_profile:
                eligibility_result = self._assess_eligibility(scheme_info, user_profile)
            else:
                # Default eligibility when no profile
                eligibility_result = {
                    "eligibility_score": 0.5,
                    "is_eligible": True,
                    "eligibility_reasons": ["Profile not provided for assessment"],
                    "ineligibility_reasons": [],
                }

            # Calculate priority score (relevance + eligibility)
            priority_score = (similarity_score * 0.6) + (
                eligibility_result["eligibility_score"] * 0.4
            )

            # Get state from metadata for better filtering
            scheme_state = metadata.get("state", "")
            source_doc = metadata.get("source", "")

            # Append state to source_document for filtering
            if scheme_state and scheme_state != "All India":
                source_doc = f"{source_doc} ({scheme_state})"

            # Create recommendation
            recommendation = SchemeRecommendation(
                scheme_id=document.get("id", ""),
                scheme_name=scheme_info.get(
                    "scheme_name", metadata.get("scheme_name", "Unknown")
                ),
                scheme_type=scheme_info.get(
                    "scheme_type", metadata.get("scheme_type", "Central")
                ),
                description=scheme_info.get("description", content[:200]),
                eligibility_score=eligibility_result["eligibility_score"],
                is_eligible=eligibility_result["is_eligible"],
                eligibility_reasons=eligibility_result["eligibility_reasons"],
                ineligibility_reasons=eligibility_result["ineligibility_reasons"],
                benefits=scheme_info.get("benefits", []),
                application_procedure=self._format_list_to_string(
                    scheme_info.get("application_procedure", [])
                ),
                required_documents=scheme_info.get("required_documents", []),
                application_deadline=scheme_info.get("application_deadline"),
                contact_information=scheme_info.get("contact_information"),
                source_document=source_doc,
                location_specific=scheme_info.get("location_specific", False),
                priority_score=priority_score,
            )

            return recommendation

        except Exception as e:
            logger.error(f"Failed to process scheme document: {e}")
            return None

    def _parse_scheme_content(
        self,
        content: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse structured scheme content directly (no LLM calls)."""
        try:
            lines = content.split("\n")

            scheme_name = metadata.get("scheme_name", "Unknown Scheme")
            scheme_type = metadata.get("scheme_type", "Central")
            description = ""
            benefits = []
            eligibility_criteria = []
            application_procedure = []
            required_documents = []

            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Identify sections
                if line.startswith("Description:"):
                    current_section = "description"
                    continue
                elif line.startswith("Benefits:"):
                    current_section = "benefits"
                    continue
                elif line.startswith("Eligibility:"):
                    current_section = "eligibility"
                    continue
                elif line.startswith("Application Process:") or line.startswith(
                    "Application Procedure:"
                ):
                    current_section = "application"
                    continue
                elif line.startswith("Required Documents:"):
                    current_section = "documents"
                    continue
                elif (
                    line.startswith("Type:")
                    or line.startswith("Category:")
                    or line.startswith("State:")
                ):
                    current_section = None
                    continue

                # Add content to appropriate section
                if current_section == "description" and line:
                    description += line + " "
                elif current_section == "benefits" and line.startswith("-"):
                    benefits.append(line[1:].strip())
                elif current_section == "eligibility" and line.startswith("-"):
                    eligibility_criteria.append(line[1:].strip())
                elif current_section == "application" and line.startswith(
                    ("-", "1.", "2.", "3.", "4.")
                ):
                    clean_line = line.lstrip("0123456789.-").strip()
                    if clean_line:
                        application_procedure.append(clean_line)
                elif current_section == "documents" and line.startswith("-"):
                    required_documents.append(line[1:].strip())

            # Default values if parsing failed
            if not description:
                description = content[:200] + "..."

            if not benefits:
                benefits = ["Benefits information available in scheme details"]

            if not eligibility_criteria:
                eligibility_criteria = ["See scheme details for eligibility criteria"]

            if not application_procedure:
                application_procedure = [
                    "Visit official portal or contact local authorities"
                ]

            if not required_documents:
                required_documents = ["Aadhaar Card", "Bank Account Details"]

            return {
                "scheme_name": scheme_name,
                "scheme_type": scheme_type,
                "description": description.strip(),
                "benefits": benefits,
                "eligibility_criteria": eligibility_criteria,
                "application_procedure": application_procedure,
                "required_documents": required_documents,
                "application_deadline": None,
                "contact_information": None,
                "location_specific": metadata.get("state", "All India") != "All India",
            }

        except Exception as e:
            logger.error(f"Failed to parse scheme content: {e}")
            return {
                "scheme_name": metadata.get("scheme_name", "Unknown Scheme"),
                "scheme_type": metadata.get("scheme_type", "Central"),
                "description": content[:200] + "...",
                "benefits": ["Benefits information available"],
                "eligibility_criteria": ["See scheme details"],
                "application_procedure": ["Contact local authorities"],
                "required_documents": ["Aadhaar Card", "Bank Account Details"],
                "application_deadline": None,
                "contact_information": None,
                "location_specific": False,
            }

    def _filter_by_state(
        self,
        recommendations: List[SchemeRecommendation],
        user_profile: UserProfile,
    ) -> List[SchemeRecommendation]:
        """Filter schemes by user's state - show state schemes + central schemes."""
        if not user_profile.location or not user_profile.location.get("state"):
            # No state in profile - show only Central schemes
            return [r for r in recommendations if r.scheme_type == "Central"]

        user_state = user_profile.location["state"].lower().strip()
        filtered = []

        for rec in recommendations:
            if rec.scheme_type == "State":
                # Try to extract state from multiple sources
                scheme_state = None

                # Method 1: Check source_document metadata (most reliable)
                if rec.source_document:
                    # Source document might contain state info
                    source_lower = rec.source_document.lower()
                    if user_state in source_lower:
                        scheme_state = user_state

                # Method 2: Extract from description (in parentheses)
                if not scheme_state:
                    desc_lower = rec.description.lower()
                    if "(" in desc_lower and ")" in desc_lower:
                        start = desc_lower.find("(")
                        end = desc_lower.find(")", start)
                        extracted_state = desc_lower[start + 1 : end].strip()

                        # Check if extracted state matches user state
                        if (
                            extracted_state == user_state
                            or user_state in extracted_state
                        ):
                            scheme_state = user_state

                # Method 3: Check scheme name for state
                if not scheme_state:
                    name_lower = rec.scheme_name.lower()
                    if user_state in name_lower:
                        scheme_state = user_state

                # Include if state matches
                if scheme_state == user_state:
                    filtered.append(rec)
                    logger.debug(
                        f"Including state scheme: {rec.scheme_name} for {user_state}"
                    )
            else:
                # Include all non-State schemes (Central, Loan, Insurance, etc.)
                filtered.append(rec)
                logger.debug(f"Including {rec.scheme_type} scheme: {rec.scheme_name}")

        logger.info(
            f"Filtered schemes: {len(filtered)} out of {len(recommendations)} for state: {user_state}"
        )
        return filtered

    def _assess_eligibility(
        self,
        scheme_info: Dict[str, Any],
        user_profile: UserProfile,
    ) -> Dict[str, Any]:
        """Simple eligibility assessment based on basic criteria."""
        try:
            eligibility_reasons = []
            ineligibility_reasons = []

            # Extract eligibility criteria
            criteria = scheme_info.get("eligibility_criteria", [])
            criteria_text = " ".join(criteria).lower() if criteria else ""

            # Basic checks
            score = 0.7  # Default score

            # Check location
            if user_profile.location and user_profile.location.get("state"):
                state = user_profile.location["state"].lower()
                if state in criteria_text or "all india" in criteria_text:
                    eligibility_reasons.append(f"Available in {state.title()}")
                    score += 0.1

            # Check farmer category
            if user_profile.farmer_category:
                category = user_profile.farmer_category.lower()
                if category in criteria_text or "all farmers" in criteria_text:
                    eligibility_reasons.append(f"Applicable for {category} farmers")
                    score += 0.1

            # Check documents
            if user_profile.has_aadhaar and "aadhaar" in criteria_text:
                eligibility_reasons.append("Has Aadhaar card")
                score += 0.05

            if user_profile.has_bank_account and "bank" in criteria_text:
                eligibility_reasons.append("Has bank account")
                score += 0.05

            # Cap score at 1.0
            score = min(score, 1.0)

            # Determine eligibility
            is_eligible = score >= 0.6

            if not eligibility_reasons:
                eligibility_reasons = ["Basic eligibility criteria met"]

            return {
                "eligibility_score": score,
                "is_eligible": is_eligible,
                "eligibility_reasons": eligibility_reasons,
                "ineligibility_reasons": ineligibility_reasons,
            }

        except Exception as e:
            logger.error(f"Failed to assess eligibility: {e}")
            return {
                "eligibility_score": 0.5,
                "is_eligible": False,
                "eligibility_reasons": [],
                "ineligibility_reasons": ["Unable to assess eligibility"],
            }

    def _format_list_to_string(self, items: List[str]) -> str:
        """Format list to numbered string."""
        if not items:
            return "Application procedure not specified"

        if isinstance(items, str):
            return items

        # Number the steps
        steps = [f"{i+1}. {step}" for i, step in enumerate(items)]
        return " ".join(steps)

    async def _translate_schemes(
        self,
        schemes: List[SchemeRecommendation],
        target_language: str,
    ) -> List[SchemeRecommendation]:
        """
        Translate schemes to target language.

        Args:
            schemes: List of scheme recommendations
            target_language: Target language code (e.g., 'hi', 'te', 'pa')

        Returns:
            List of translated scheme recommendations
        """
        try:
            logger.info(f"Translating {len(schemes)} schemes to {target_language}")

            translated_schemes = []

            for scheme in schemes:
                try:
                    # Translate scheme name
                    translated_name = await translation_service.translate_text(
                        text=scheme.scheme_name,
                        source_lang="en",
                        target_lang=target_language,
                        use_cache=True,
                    )

                    # Translate description
                    translated_description = await translation_service.translate_text(
                        text=scheme.description,
                        source_lang="en",
                        target_lang=target_language,
                        use_cache=True,
                    )

                    # Translate benefits (batch)
                    if scheme.benefits:
                        translated_benefits = []
                        for benefit in scheme.benefits:
                            translated_benefit = (
                                await translation_service.translate_text(
                                    text=benefit,
                                    source_lang="en",
                                    target_lang=target_language,
                                    use_cache=True,
                                )
                            )
                            translated_benefits.append(translated_benefit)
                    else:
                        translated_benefits = scheme.benefits

                    # Translate eligibility reasons
                    if scheme.eligibility_reasons:
                        translated_eligibility = []
                        for reason in scheme.eligibility_reasons:
                            translated_reason = (
                                await translation_service.translate_text(
                                    text=reason,
                                    source_lang="en",
                                    target_lang=target_language,
                                    use_cache=True,
                                )
                            )
                            translated_eligibility.append(translated_reason)
                    else:
                        translated_eligibility = scheme.eligibility_reasons

                    # Create translated scheme
                    translated_scheme = SchemeRecommendation(
                        scheme_id=scheme.scheme_id,
                        scheme_name=translated_name,
                        scheme_type=scheme.scheme_type,
                        description=translated_description,
                        eligibility_score=scheme.eligibility_score,
                        is_eligible=scheme.is_eligible,
                        eligibility_reasons=translated_eligibility,
                        ineligibility_reasons=scheme.ineligibility_reasons,
                        benefits=translated_benefits,
                        application_procedure=scheme.application_procedure,
                        required_documents=scheme.required_documents,
                        application_deadline=scheme.application_deadline,
                        contact_information=scheme.contact_information,
                        source_document=scheme.source_document,
                        location_specific=scheme.location_specific,
                        priority_score=scheme.priority_score,
                    )

                    translated_schemes.append(translated_scheme)

                except Exception as e:
                    logger.warning(
                        f"Failed to translate scheme {scheme.scheme_name}: {e}"
                    )
                    # If translation fails, use original scheme
                    translated_schemes.append(scheme)

            logger.info(f"Successfully translated {len(translated_schemes)} schemes")
            return translated_schemes

        except Exception as e:
            logger.error(f"Failed to translate schemes: {e}")
            # Return original schemes if translation fails
            return schemes


# Global instance
scheme_service = SchemeService()
