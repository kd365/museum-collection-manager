"""AI service for generating artwork and collection descriptions using AWS Bedrock."""

import json
import logging
import boto3
from flask import current_app

logger = logging.getLogger(__name__)


def get_bedrock_client():
    """Create a Bedrock Runtime client using the configured AWS profile."""
    try:
        session = boto3.Session(
            profile_name=current_app.config.get('AWS_PROFILE', 'cyber-risk'),
            region_name=current_app.config.get('BEDROCK_REGION', 'us-east-1')
        )
        return session.client('bedrock-runtime')
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {e}")
        return None


def generate_artwork_description(artwork):
    """Generate an AI description for an artwork based on its metadata."""
    client = get_bedrock_client()
    if not client:
        return None

    artist_name = artwork.artist.name if artwork.artist else "Unknown artist"

    details = [f"Title: {artwork.title}", f"Artist: {artist_name}"]
    if artwork.medium:
        details.append(f"Medium: {artwork.medium}")
    if artwork.art_movement:
        details.append(f"Art Movement: {artwork.art_movement}")
    if artwork.subject:
        details.append(f"Subject: {artwork.subject}")
    if artwork.creation_date:
        details.append(f"Created: {artwork.creation_date}")
    if artwork.dimension_H and artwork.dimension_W:
        dims = f"{artwork.dimension_H} x {artwork.dimension_W}"
        if artwork.dimension_D:
            dims += f" x {artwork.dimension_D}"
        dims += f" {artwork.dimension_unit}"
        details.append(f"Dimensions: {dims}")
    if artwork.estimated_value:
        details.append(f"Estimated Value: ${artwork.estimated_value:,.2f}")
    if artwork.is_signed:
        details.append(f"Signed: Yes ({artwork.signature_location or 'location unspecified'})")

    prompt = f"""You are a knowledgeable art curator writing a museum placard description.
Based on the following artwork details, write a compelling 2-3 sentence description
that a museum visitor would find informative and engaging. Focus on the artistic
significance, technique, and historical context.

{chr(10).join(details)}

Write only the description. No preamble or headers."""

    try:
        response = client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        result = json.loads(response["body"].read())
        description = result["content"][0]["text"]
        logger.info(f"Generated description for artwork '{artwork.title}'")
        return description
    except Exception as e:
        logger.error(f"Bedrock error generating artwork description: {e}")
        return None


def generate_collection_description(museum, artworks):
    """Generate an AI description of a museum's collection when it has 5+ artworks."""
    client = get_bedrock_client()
    if not client:
        return None

    artwork_summaries = []
    for aw in artworks:
        artist_name = aw.artist.name if aw.artist else "Unknown"
        summary = f"- \"{aw.title}\" by {artist_name}"
        if aw.medium:
            summary += f" ({aw.medium})"
        if aw.art_movement:
            summary += f", {aw.art_movement}"
        artwork_summaries.append(summary)

    prompt = f"""You are a museum curator writing a collection overview for the {museum.name} in {museum.city}, {museum.country}.
The museum currently holds {len(artworks)} artworks in its collection:

{chr(10).join(artwork_summaries)}

Write a 3-4 sentence collection overview that highlights the themes, artistic
movements, and notable pieces. This will be displayed on the museum's collection
page. Write in a professional, engaging tone suitable for museum visitors.

Write only the description. No preamble or headers."""

    try:
        response = client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        result = json.loads(response["body"].read())
        description = result["content"][0]["text"]
        logger.info(f"Generated collection description for '{museum.name}'")
        return description
    except Exception as e:
        logger.error(f"Bedrock error generating collection description: {e}")
        return None
