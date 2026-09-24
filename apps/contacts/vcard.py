def escape_vcard_text(value):
    """
    # FIX: RFC 2426 / RFC 6350 escaping for vCard text values.
    Backslashes, semicolons, and commas must be prefixed with a backslash.
    """
    if not value:
        return ""
    val_str = str(value)
    # Escape backslash first to prevent double-escaping
    val_str = val_str.replace('\\', r'\\')
    val_str = val_str.replace(';', r'\;')
    val_str = val_str.replace(',', r'\,')
    return val_str


def generate_vcard_content(profile, request=None):
    """
    Generates a standard vCard 3.0 string for the creator's profile,
    respecting privacy settings (only exposing public data).
    """
    fn_escaped = escape_vcard_text(profile.display_name)
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{fn_escaped}",
    ]

    # Name parts (Last;First;Middle;Prefix;Suffix)
    names = profile.display_name.strip().split(None, 1)
    if len(names) == 2:
        last_escaped = escape_vcard_text(names[1])
        first_escaped = escape_vcard_text(names[0])
        lines.append(f"N:{last_escaped};{first_escaped};;;")
    else:
        lines.append(f"N:{fn_escaped};;;;")

    if getattr(profile, 'title_tagline', None):
        lines.append(f"TITLE:{escape_vcard_text(profile.title_tagline)}")

    if profile.bio:
        # Sanitize single-line note for vCard, preserving newline stripping, then escape
        clean_bio = profile.bio.replace("\r\n", " ").replace("\n", " ")
        lines.append(f"NOTE:{escape_vcard_text(clean_bio)}")

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
