"""add ipeds data fields and completeness scoring

Revision ID: XXXXXX_ipeds_data
Revises: <previous_revision>
Create Date: 2025-11-26

This migration adds:
1. IPEDS data fields to institutions table (cost, admissions)
2. institution_data_verifications table for tracking admin updates
3. Completeness score calculation function and trigger
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'XXXXXX_ipeds_data'
down_revision = '<previous_revision>'  # Update this with your latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================================================
    # STEP 1: Add IPEDS columns to institutions table
    # ========================================================================
    
    # Data tracking fields
    op.add_column('institutions', sa.Column('data_completeness_score', sa.Integer(), server_default='0', nullable=False))
    op.add_column('institutions', sa.Column('data_last_updated', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('institutions', sa.Column('data_source', sa.String(length=50), server_default='ipeds', nullable=False))
    op.add_column('institutions', sa.Column('ipeds_year', sa.String(length=10), server_default='2023-24', nullable=True))
    op.add_column('institutions', sa.Column('is_featured', sa.Boolean(), server_default='false', nullable=False))
    
    # Cost data fields
    op.add_column('institutions', sa.Column('tuition_in_state', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('tuition_out_of_state', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('tuition_private', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('tuition_in_district', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('room_cost', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('board_cost', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('room_and_board', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('application_fee_undergrad', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('institutions', sa.Column('application_fee_grad', sa.DECIMAL(10, 2), nullable=True))
    
    # Admissions data fields
    op.add_column('institutions', sa.Column('acceptance_rate', sa.DECIMAL(5, 2), nullable=True))
    op.add_column('institutions', sa.Column('sat_reading_25th', sa.SmallInteger(), nullable=True))
    op.add_column('institutions', sa.Column('sat_reading_75th', sa.SmallInteger(), nullable=True))
    op.add_column('institutions', sa.Column('sat_math_25th', sa.SmallInteger(), nullable=True))
    op.add_column('institutions', sa.Column('sat_math_75th', sa.SmallInteger(), nullable=True))
    op.add_column('institutions', sa.Column('act_composite_25th', sa.SmallInteger(), nullable=True))
    op.add_column('institutions', sa.Column('act_composite_75th', sa.SmallInteger(), nullable=True))
    
    # Create indexes for performance
    op.create_index('idx_institutions_completeness', 'institutions', ['data_completeness_score'], unique=False, postgresql_ops={'data_completeness_score': 'DESC'})
    op.create_index('idx_institutions_featured', 'institutions', ['is_featured'], unique=False, postgresql_where=sa.text('is_featured = true'))
    op.create_index('idx_institutions_data_source', 'institutions', ['data_source'], unique=False)
    
    # ========================================================================
    # STEP 2: Create institution_data_verifications table
    # ========================================================================
    
    op.create_table('institution_data_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('previous_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('data_source', sa.String(length=50), server_default='admin_update', nullable=False),
        sa.Column('verified_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('academic_year', sa.String(length=10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.CheckConstraint(
            "field_name IN ('tuition_in_state', 'tuition_out_of_state', 'tuition_private', 'room_cost', 'board_cost', 'acceptance_rate', 'sat_reading_25th', 'sat_math_25th', 'act_composite_25th')",
            name='valid_field_name'
        ),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_verifications_institution', 'institution_data_verifications', ['institution_id'], unique=False)
    op.create_index('idx_verifications_date', 'institution_data_verifications', ['verified_at'], unique=False, postgresql_ops={'verified_at': 'DESC'})
    
    # ========================================================================
    # STEP 3: Create completeness score calculation function
    # ========================================================================
    
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_completeness_score(inst_id INTEGER)
        RETURNS INTEGER AS $$
        DECLARE
          score INTEGER := 0;
          inst_record RECORD;
          image_count INTEGER;
        BEGIN
          SELECT * INTO inst_record FROM institutions WHERE id = inst_id;
          
          IF NOT FOUND THEN RETURN 0; END IF;
          
          -- Core Identity (20 points)
          IF inst_record.name IS NOT NULL THEN score := score + 5; END IF;
          IF inst_record.city IS NOT NULL AND inst_record.state IS NOT NULL THEN 
            score := score + 5; 
          END IF;
          IF inst_record.website IS NOT NULL THEN score := score + 10; END IF;
          
          -- Cost Data (40 points)
          IF inst_record.control = 1 THEN
            -- Public institution
            IF inst_record.tuition_in_state IS NOT NULL AND inst_record.tuition_in_state > 0 THEN
              score := score + 10;
            END IF;
            IF inst_record.tuition_out_of_state IS NOT NULL AND inst_record.tuition_out_of_state > 0 THEN
              score := score + 10;
            END IF;
          ELSIF inst_record.control IN (2, 3) THEN
            -- Private institution
            IF inst_record.tuition_private IS NOT NULL AND inst_record.tuition_private > 0 THEN
              score := score + 20;
            END IF;
          END IF;
          
          -- Room & Board (20 points)
          IF (inst_record.room_cost IS NOT NULL AND inst_record.room_cost > 0) OR
             (inst_record.board_cost IS NOT NULL AND inst_record.board_cost > 0) OR
             (inst_record.room_and_board IS NOT NULL AND inst_record.room_and_board > 0) THEN
            score := score + 20;
          END IF;
          
          -- Admissions Data (10 points)
          IF inst_record.acceptance_rate IS NOT NULL THEN score := score + 5; END IF;
          IF inst_record.sat_math_25th IS NOT NULL OR inst_record.act_composite_25th IS NOT NULL THEN
            score := score + 5;
          END IF;
          
          -- Images (30 points) - Check entity_images table
          SELECT COUNT(*) INTO image_count 
          FROM entity_images 
          WHERE entity_type = 'institution' AND entity_id = inst_id;
          
          IF image_count > 0 THEN score := score + 15; END IF;
          IF image_count >= 3 THEN score := score + 15; END IF;
          
          -- Admin Verification Bonus (10 points)
          IF inst_record.data_source = 'admin' OR inst_record.data_source = 'mixed' THEN
            score := score + 10;
          END IF;
          
          IF score > 100 THEN score := 100; END IF;
          
          RETURN score;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # ========================================================================
    # STEP 4: Create trigger to auto-update completeness score
    # ========================================================================
    
    op.execute("""
        CREATE OR REPLACE FUNCTION update_completeness_score_trigger()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.data_completeness_score := calculate_completeness_score(NEW.id);
          NEW.data_last_updated := CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_update_completeness
        BEFORE UPDATE ON institutions
        FOR EACH ROW
        WHEN (
          OLD.name IS DISTINCT FROM NEW.name OR
          OLD.city IS DISTINCT FROM NEW.city OR
          OLD.tuition_in_state IS DISTINCT FROM NEW.tuition_in_state OR
          OLD.tuition_private IS DISTINCT FROM NEW.tuition_private OR
          OLD.room_cost IS DISTINCT FROM NEW.room_cost OR
          OLD.acceptance_rate IS DISTINCT FROM NEW.acceptance_rate OR
          OLD.data_source IS DISTINCT FROM NEW.data_source
        )
        EXECUTE FUNCTION update_completeness_score_trigger();
    """)


def downgrade() -> None:
    # Drop trigger and functions
    op.execute("DROP TRIGGER IF EXISTS trigger_update_completeness ON institutions;")
    op.execute("DROP FUNCTION IF EXISTS update_completeness_score_trigger();")
    op.execute("DROP FUNCTION IF EXISTS calculate_completeness_score(INTEGER);")
    
    # Drop institution_data_verifications table
    op.drop_index('idx_verifications_date', table_name='institution_data_verifications')
    op.drop_index('idx_verifications_institution', table_name='institution_data_verifications')
    op.drop_table('institution_data_verifications')
    
    # Drop indexes from institutions
    op.drop_index('idx_institutions_data_source', table_name='institutions')
    op.drop_index('idx_institutions_featured', table_name='institutions')
    op.drop_index('idx_institutions_completeness', table_name='institutions')
    
    # Drop columns from institutions (in reverse order)
    op.drop_column('institutions', 'act_composite_75th')
    op.drop_column('institutions', 'act_composite_25th')
    op.drop_column('institutions', 'sat_math_75th')
    op.drop_column('institutions', 'sat_math_25th')
    op.drop_column('institutions', 'sat_reading_75th')
    op.drop_column('institutions', 'sat_reading_25th')
    op.drop_column('institutions', 'acceptance_rate')
    op.drop_column('institutions', 'application_fee_grad')
    op.drop_column('institutions', 'application_fee_undergrad')
    op.drop_column('institutions', 'room_and_board')
    op.drop_column('institutions', 'board_cost')
    op.drop_column('institutions', 'room_cost')
    op.drop_column('institutions', 'tuition_in_district')
    op.drop_column('institutions', 'tuition_private')
    op.drop_column('institutions', 'tuition_out_of_state')
    op.drop_column('institutions', 'tuition_in_state')
    op.drop_column('institutions', 'is_featured')
    op.drop_column('institutions', 'ipeds_year')
    op.drop_column('institutions', 'data_source')
    op.drop_column('institutions', 'data_last_updated')
    op.drop_column('institutions', 'data_completeness_score')
