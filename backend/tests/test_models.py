"""
Tests for database models and relationships
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import (
    User, PlatformConfig, SystemConfig, 
    RecordingSchedule, Recording, RecordingJob
)


class TestUserModel:
    """Test User model CRUD operations"""
    
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a new user"""
        user = User(
            username="testuser",
            password_hash="hashed_password",
            is_admin=False
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.password_hash == "hashed_password"
        assert user.is_admin is False
        assert user.is_active is True
        assert user.created_at is not None
    
    async def test_user_unique_username(self, db_session: AsyncSession, sample_user: User):
        """Test that username must be unique"""
        duplicate_user = User(
            username=sample_user.username,
            password_hash="another_hash",
            is_admin=False
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            await db_session.commit()


class TestPlatformConfigModel:
    """Test PlatformConfig model CRUD operations"""
    
    async def test_create_platform_config(self, db_session: AsyncSession):
        """Test creating a new platform configuration"""
        config = PlatformConfig(
            platform_name="youtube",
            api_key="test_api_key",
            client_id="test_client_id",
            client_secret="test_client_secret",
            additional_settings={"quality": "best"},
            enabled=True
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        assert config.id is not None
        assert config.platform_name == "youtube"
        assert config.api_key == "test_api_key"
        assert config.additional_settings == {"quality": "best"}
        assert config.enabled is True
    
    async def test_platform_config_unique_name(self, db_session: AsyncSession, sample_platform_config: PlatformConfig):
        """Test that platform name must be unique"""
        duplicate_config = PlatformConfig(
            platform_name=sample_platform_config.platform_name,
            api_key="another_key",
            enabled=True
        )
        db_session.add(duplicate_config)
        
        with pytest.raises(Exception):
            await db_session.commit()


class TestSystemConfigModel:
    """Test SystemConfig model CRUD operations"""
    
    async def test_create_system_config(self, db_session: AsyncSession):
        """Test creating a new system configuration"""
        config = SystemConfig(
            key="max_file_size",
            value="1073741824",  # 1GB in bytes
            description="Maximum file size for recordings",
            category="storage"
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        assert config.id is not None
        assert config.key == "max_file_size"
        assert config.value == "1073741824"
        assert config.description == "Maximum file size for recordings"
        assert config.category == "storage"
    
    async def test_system_config_unique_key(self, db_session: AsyncSession):
        """Test that config key must be unique"""
        config1 = SystemConfig(key="test_key", value="value1")
        config2 = SystemConfig(key="test_key", value="value2")
        
        db_session.add(config1)
        await db_session.commit()
        
        db_session.add(config2)
        with pytest.raises(Exception):
            await db_session.commit()


class TestRecordingScheduleModel:
    """Test RecordingSchedule model CRUD operations"""
    
    async def test_create_recording_schedule(self, db_session: AsyncSession):
        """Test creating a new recording schedule"""
        schedule = RecordingSchedule(
            platform="twitch",
            streamer_id="123456",
            streamer_name="teststreamer",
            quality="best",
            output_path="/recordings",
            custom_arguments="--format mp4",
            enabled=True
        )
        db_session.add(schedule)
        await db_session.commit()
        await db_session.refresh(schedule)
        
        assert schedule.id is not None
        assert schedule.platform == "twitch"
        assert schedule.streamer_id == "123456"
        assert schedule.streamer_name == "teststreamer"
        assert schedule.quality == "best"
        assert schedule.output_path == "/recordings"
        assert schedule.custom_arguments == "--format mp4"
        assert schedule.enabled is True


class TestRecordingModel:
    """Test Recording model CRUD operations"""
    
    async def test_create_recording(self, db_session: AsyncSession, sample_recording_schedule: RecordingSchedule):
        """Test creating a new recording"""
        recording = Recording(
            schedule_id=sample_recording_schedule.id,
            file_path="/recordings/test.mp4",
            file_name="test.mp4",
            file_size=1024000,
            duration=3600.0,
            start_time=datetime.now(),
            platform="twitch",
            streamer_id="123456",
            streamer_name="teststreamer",
            status="completed",
            is_favorite=False
        )
        db_session.add(recording)
        await db_session.commit()
        await db_session.refresh(recording)
        
        assert recording.id is not None
        assert recording.schedule_id == sample_recording_schedule.id
        assert recording.file_path == "/recordings/test.mp4"
        assert recording.file_size == 1024000
        assert recording.duration == 3600.0
        assert recording.is_favorite is False
        assert recording.status == "completed"


class TestRecordingJobModel:
    """Test RecordingJob model CRUD operations"""
    
    async def test_create_recording_job(self, db_session: AsyncSession, sample_recording_schedule: RecordingSchedule):
        """Test creating a new recording job"""
        job = RecordingJob(
            schedule_id=sample_recording_schedule.id,
            status="running",
            start_time=datetime.now(),
            pid=12345
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.id is not None
        assert job.schedule_id == sample_recording_schedule.id
        assert job.status == "running"
        assert job.pid == 12345
        assert job.start_time is not None
        assert job.end_time is None


class TestModelRelationships:
    """Test model relationships and cascading behavior"""
    
    async def test_recording_schedule_relationships(self, db_session: AsyncSession, sample_recording_schedule: RecordingSchedule):
        """Test that RecordingSchedule has relationships to Recording and RecordingJob"""
        # Create related recordings and jobs
        recording = Recording(
            schedule_id=sample_recording_schedule.id,
            file_path="/recordings/test1.mp4",
            file_name="test1.mp4",
            start_time=datetime.now(),
            platform="twitch",
            streamer_id="123456",
            streamer_name="teststreamer",
            status="completed"
        )
        
        job = RecordingJob(
            schedule_id=sample_recording_schedule.id,
            status="completed",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        db_session.add_all([recording, job])
        await db_session.commit()
        await db_session.refresh(sample_recording_schedule)
        
        # Test relationships
        assert len(sample_recording_schedule.recordings) == 1
        assert len(sample_recording_schedule.jobs) == 1
        assert sample_recording_schedule.recordings[0].id == recording.id
        assert sample_recording_schedule.jobs[0].id == job.id
    
    async def test_cascade_delete(self, db_session: AsyncSession, sample_recording_schedule: RecordingSchedule):
        """Test that deleting a schedule cascades to related recordings and jobs"""
        # Create related records
        recording = Recording(
            schedule_id=sample_recording_schedule.id,
            file_path="/recordings/test2.mp4",
            file_name="test2.mp4",
            start_time=datetime.now(),
            platform="twitch",
            streamer_id="123456",
            streamer_name="teststreamer",
            status="completed"
        )
        
        job = RecordingJob(
            schedule_id=sample_recording_schedule.id,
            status="completed",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        db_session.add_all([recording, job])
        await db_session.commit()
        
        # Delete the schedule
        await db_session.delete(sample_recording_schedule)
        await db_session.commit()
        
        # Verify related records are also deleted
        result = await db_session.execute(select(Recording).where(Recording.id == recording.id))
        assert result.scalar_one_or_none() is None
        
        result = await db_session.execute(select(RecordingJob).where(RecordingJob.id == job.id))
        assert result.scalar_one_or_none() is None
    
    async def test_recording_relationship(self, db_session: AsyncSession, sample_recording: Recording):
        """Test that Recording has relationship to RecordingSchedule"""
        await db_session.refresh(sample_recording)
        
        assert sample_recording.schedule is not None
        assert sample_recording.schedule.id == sample_recording.schedule_id
    
    async def test_recording_job_relationship(self, db_session: AsyncSession, sample_recording_job: RecordingJob):
        """Test that RecordingJob has relationship to RecordingSchedule"""
        await db_session.refresh(sample_recording_job)
        
        assert sample_recording_job.schedule is not None
        assert sample_recording_job.schedule.id == sample_recording_job.schedule_id
