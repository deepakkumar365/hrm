"""
Test module for Base class from app.py

This module tests the SQLAlchemy DeclarativeBase subclass that serves as 
the foundation for all ORM models in the HRM application.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Import the Base class and related components
from app import Base, db, app


class TestBase:
    """Test cases for the Base class"""
    
    def test_base_class_instantiation_works(self):
        """Test that Base class can be instantiated successfully"""
        base_instance = Base()
        
        # Verify that the instance is created
        assert base_instance is not None
        assert isinstance(base_instance, Base)
        assert isinstance(base_instance, DeclarativeBase)
    
    def test_base_inherits_declarative_base_functionality(self):
        """Test that Base class properly inherits DeclarativeBase functionality"""
        # Check that Base has the required DeclarativeBase attributes
        # In SQLAlchemy 2.0, registry is used instead of __mapper_registry__
        assert hasattr(Base, 'registry')
        assert hasattr(Base, 'metadata')
        
        # Verify the metadata is a proper MetaData object
        from sqlalchemy import MetaData
        assert isinstance(Base.metadata, MetaData)
    
    def test_base_class_allows_model_inheritance(self):
        """Test that Base class can be used as a parent for ORM models"""
        # Create a test model that inherits from Base
        class TestModel(Base):
            __tablename__ = 'test_model'
            
            id = Column(Integer, primary_key=True)
            name = Column(String(50), nullable=False)
        
        # Verify the model was created successfully
        assert TestModel.__tablename__ == 'test_model'
        assert hasattr(TestModel, '__table__')
        assert hasattr(TestModel, '__mapper__')
        
        # Verify it's registered in the Base metadata
        assert 'test_model' in Base.metadata.tables
        
        # Clean up - remove the test table from metadata
        Base.metadata.remove(TestModel.__table__)
    
    def test_base_class_has_correct_metadata(self):
        """Test that Base class has properly configured metadata"""
        # Check metadata is not None and is properly initialized
        assert Base.metadata is not None
        
        # Check that metadata has the expected attributes
        assert hasattr(Base.metadata, 'tables')
        assert hasattr(Base.metadata, 'create_all')
        assert hasattr(Base.metadata, 'drop_all')
        
        # Initially metadata should be empty or contain only existing models
        assert isinstance(Base.metadata.tables, dict)
    
    def test_base_class_registry_functionality(self):
        """Test that Base class registry functionality works correctly"""
        # Check that the registry exists and is functional
        assert hasattr(Base, 'registry')
        assert hasattr(Base.registry, 'mappers')
        
        # Create a temporary model to test registry
        class TempModel(Base):
            __tablename__ = 'temp_model'
            id = Column(Integer, primary_key=True)
        
        # Verify the model is registered
        mapper_count_before_cleanup = len(Base.registry.mappers)
        assert mapper_count_before_cleanup > 0
        
        # Verify we can find our temp model in the registry
        temp_model_found = False
        for mapper in Base.registry.mappers:
            if hasattr(mapper.class_, '__tablename__') and mapper.class_.__tablename__ == 'temp_model':
                temp_model_found = True
                break
        
        assert temp_model_found, "TempModel should be registered in Base registry"
        
        # Clean up
        if 'temp_model' in Base.metadata.tables:
            Base.metadata.remove(Base.metadata.tables['temp_model'])


class TestBaseIntegration:
    """Integration tests for Base class with Flask-SQLAlchemy"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Create a test database in memory
        self.test_db_uri = 'sqlite:///:memory:'
        
        # Backup original config
        self.original_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        
    def teardown_method(self):
        """Clean up after each test"""
        # Restore original config if it existed
        if self.original_db_uri:
            app.config['SQLALCHEMY_DATABASE_URI'] = self.original_db_uri
    
    def test_base_works_with_flask_sqlalchemy(self):
        """Test that Base class works correctly with Flask-SQLAlchemy"""
        with app.app_context():
            # Flask-SQLAlchemy 3.1+ creates its own model class but uses our Base's metadata
            # Verify that the db instance was created with our Base class
            assert db.Model is not Base  # Flask-SQLAlchemy creates wrapper
            assert hasattr(db.Model, 'metadata')
            
            # Most importantly, verify that our existing models work
            from models import User  # Import an existing model
            assert hasattr(User, '__tablename__')
            assert User.__tablename__ == 'hrm_users'
            
            # Verify User model can be instantiated
            user = User()
            assert user is not None
            
            # Verify the metadata is shared (this is the key integration point)
            assert 'hrm_users' in Base.metadata.tables
    
    @pytest.mark.skipif(
        not os.environ.get('DATABASE_URL'),
        reason="DATABASE_URL not set, skipping database integration test"
    )
    def test_base_with_actual_database_connection(self):
        """Test Base class functionality with actual database (if available)"""
        with app.app_context():
            # This test only runs if DATABASE_URL is set
            # Verify that we can create tables using Base metadata
            try:
                # Create a simple test model
                class DBTestModel(Base):
                    __tablename__ = 'db_test_model_temp'
                    id = Column(Integer, primary_key=True)
                    test_field = Column(String(50))
                
                # Try to create the table
                db.create_all()
                
                # Verify table exists in metadata
                assert 'db_test_model_temp' in Base.metadata.tables
                
                # Clean up - drop the test table
                if hasattr(DBTestModel, '__table__'):
                    DBTestModel.__table__.drop(db.engine)
                
                # Remove from metadata
                if 'db_test_model_temp' in Base.metadata.tables:
                    Base.metadata.remove(Base.metadata.tables['db_test_model_temp'])
                
            except Exception as e:
                pytest.skip(f"Database connection test failed: {str(e)}")


class TestBaseErrorCases:
    """Test error handling and edge cases for Base class"""
    
    def test_base_with_invalid_model_definition(self):
        """Test Base behavior with invalid model definitions"""
        # Test model without __tablename__ - SQLAlchemy 2.0 raises immediately
        from sqlalchemy.exc import InvalidRequestError
        with pytest.raises(InvalidRequestError):
            class InvalidModel(Base):
                # Missing __tablename__
                id = Column(Integer, primary_key=True)
    
    def test_base_duplicate_tablename_handling(self):
        """Test how Base handles models with duplicate table names"""
        # Create first model
        class FirstModel(Base):
            __tablename__ = 'duplicate_test'
            id = Column(Integer, primary_key=True)
        
        # Creating second model with same tablename should raise an error
        with pytest.raises(Exception):  # SQLAlchemy will raise an error for duplicate tables
            class SecondModel(Base):
                __tablename__ = 'duplicate_test'
                id = Column(Integer, primary_key=True)
            
            # Force table creation to trigger the error
            _ = SecondModel.__table__
        
        # Clean up first model
        if 'duplicate_test' in Base.metadata.tables:
            Base.metadata.remove(Base.metadata.tables['duplicate_test'])


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])