@pytest.fixture
async def test_scholarship(db_session: AsyncSession) -> Scholarship:
    """Create a test scholarship - use valid enum values"""
    scholarship = Scholarship(
        title=f"Test Scholarship {random.randint(1000, 9999)}",
        organization="Test Organization",
        scholarship_type="ACADEMIC_MERIT",  # Valid enum: ACADEMIC_MERIT
        status="ACTIVE",                     # Valid enum: ACTIVE
        difficulty_level="MODERATE",         # Valid enum: MODERATE
        amount_min=1000,
        amount_max=5000,
        is_renewable=True,
        min_gpa=3.0
    )
    db_session.add(scholarship)
    await db_session.flush()
    await db_session.refresh(scholarship)
    return scholarship
