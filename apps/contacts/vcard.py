def generate_vcard_content(profile, request=None):
    """
    Generates a standard vCard 3.0 string for the creator's profile,
    respecting privacy settings (only exposing public data).
    """
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{profile.display_name}",
    ]

    # Name parts (Last;First;Middle;Prefix;Suffix)
    names = profile.display_name.strip().split(None, 1)
    if len(names) == 2:
        lines.append(f"N:{names[1]};{names[0]};;;")
    else:
        lines.append(f"N:{profile.display_name};;;;")

    if profile.bio:
        # Sanitize single-line note for vCard
        clean_bio = profile.bio.replace("\r\n", " ").replace("\n", " ")
        lines.append(f"NOTE:{clean_bio}")

    if profile.public_email:
        lines.append(f"EMAIL;TYPE=INTERNET,PREF:{profile.public_email}")

    if profile.phone:
        lines.append(f"TEL;TYPE=CELL,VOICE:{profile.phone}")

    # Build canonical profile URL
    if request:
        profile_url = request.build_absolute_uri(f"/{profile.username}/")
    else:
        profile_url = profile.website or f"/{profile.username}/"

    if profile.website:
        lines.append(f"URL;TYPE=WORK:{profile.website}")
    lines.append(f"URL;TYPE=PROFILE:{profile_url}")

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"
