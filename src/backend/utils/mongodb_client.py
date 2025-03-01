"""
Utility module that provides MongoDB client functionality and connection management 
for document storage in the Justice Bid system.
"""

import os
from typing import Dict, List, Any, Optional

import pymongo
from pymongo import MongoClient
from pymongo import errors

# Internal imports
from ..config import config
from ..utils import logging

# Configure logger
logger = logging.getLogger(__name__)

# Global singleton MongoDB client instance
_mongo_client = None

# Get MongoDB connection details from environment or config
MONGO_URI = os.getenv('MONGO_URI', config.MONGODB_URI)
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', config.MONGODB_NAME)


def get_mongo_client() -> MongoClient:
    """
    Returns a singleton MongoDB client instance, creating it if it doesn't exist.
    
    Returns:
        MongoClient: Configured MongoDB client instance
    """
    global _mongo_client
    
    if _mongo_client is None:
        try:
            logger.info(f"Initializing MongoDB connection to {MONGO_URI}")
            _mongo_client = MongoClient(MONGO_URI)
            # Test connection
            _mongo_client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
        except errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return _mongo_client


def get_database():
    """
    Returns the MongoDB database instance for the configured database name.
    
    Returns:
        Database: MongoDB database instance
    """
    client = get_mongo_client()
    return client[MONGO_DB_NAME]


def get_collection(collection_name: str):
    """
    Returns a MongoDB collection by name from the configured database.
    
    Args:
        collection_name (str): Name of the collection to retrieve
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = get_database()
    return db[collection_name]


def create_document(collection_name: str, document: Dict) -> str:
    """
    Creates a new document in the specified collection.
    
    Args:
        collection_name (str): Name of the collection
        document (dict): Document data to insert
        
    Returns:
        str: ID of the created document
    """
    try:
        collection = get_collection(collection_name)
        result = collection.insert_one(document)
        logger.debug(f"Document created in {collection_name} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except errors.PyMongoError as e:
        logger.error(f"Error creating document in {collection_name}: {str(e)}")
        raise


def get_document(collection_name: str, document_id: str) -> Optional[Dict]:
    """
    Retrieves a document by ID from the specified collection.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document to retrieve
        
    Returns:
        dict: Document data or None if not found
    """
    try:
        collection = get_collection(collection_name)
        document = collection.find_one({"_id": pymongo.ObjectId(document_id)})
        
        if document:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            logger.debug(f"Document retrieved from {collection_name}: {document_id}")
        else:
            logger.debug(f"Document not found in {collection_name}: {document_id}")
            
        return document
    except errors.PyMongoError as e:
        logger.error(f"Error retrieving document from {collection_name}: {str(e)}")
        raise


def find_documents(
    collection_name: str, 
    query_filter: Dict = None,
    projection: Dict = None,
    limit: int = 0,
    skip: int = 0,
    sort: Dict = None
) -> List[Dict]:
    """
    Finds documents in the specified collection based on query filter.
    
    Args:
        collection_name (str): Name of the collection
        query_filter (dict): MongoDB query filter
        projection (dict): Fields to include or exclude
        limit (int): Maximum number of documents to return
        skip (int): Number of documents to skip
        sort (dict): Sorting criteria
        
    Returns:
        list: List of matching documents
    """
    try:
        collection = get_collection(collection_name)
        
        # Default empty filter if none provided
        query_filter = query_filter or {}
        
        # Build cursor with options
        cursor = collection.find(query_filter, projection)
        
        if skip:
            cursor = cursor.skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
            
        if sort:
            cursor = cursor.sort(list(sort.items()))
        
        # Convert ObjectId to string and build result list
        results = []
        for document in cursor:
            if "_id" in document and isinstance(document["_id"], pymongo.ObjectId):
                document["_id"] = str(document["_id"])
            results.append(document)
        
        logger.debug(f"Found {len(results)} documents in {collection_name}")
        return results
    except errors.PyMongoError as e:
        logger.error(f"Error finding documents in {collection_name}: {str(e)}")
        raise


def update_document(
    collection_name: str, 
    document_id: str, 
    update_data: Dict,
    upsert: bool = False
) -> bool:
    """
    Updates a document by ID in the specified collection.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document to update
        update_data (dict): Data to update
        upsert (bool): Whether to insert if document doesn't exist
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        collection = get_collection(collection_name)
        
        # Use $set to avoid overwriting the entire document
        result = collection.update_one(
            {"_id": pymongo.ObjectId(document_id)},
            {"$set": update_data},
            upsert=upsert
        )
        
        success = result.modified_count > 0 or (upsert and result.upserted_id is not None)
        
        if success:
            logger.debug(f"Document updated in {collection_name}: {document_id}")
        else:
            logger.debug(f"Document not updated in {collection_name}: {document_id}")
            
        return success
    except errors.PyMongoError as e:
        logger.error(f"Error updating document in {collection_name}: {str(e)}")
        raise


def delete_document(collection_name: str, document_id: str) -> bool:
    """
    Deletes a document by ID from the specified collection.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        collection = get_collection(collection_name)
        result = collection.delete_one({"_id": pymongo.ObjectId(document_id)})
        
        success = result.deleted_count > 0
        
        if success:
            logger.debug(f"Document deleted from {collection_name}: {document_id}")
        else:
            logger.debug(f"Document not deleted from {collection_name}: {document_id}")
            
        return success
    except errors.PyMongoError as e:
        logger.error(f"Error deleting document from {collection_name}: {str(e)}")
        raise


def aggregate(collection_name: str, pipeline: List[Dict]) -> List[Dict]:
    """
    Performs an aggregation operation on the specified collection.
    
    Args:
        collection_name (str): Name of the collection
        pipeline (list): Aggregation pipeline stages
        
    Returns:
        list: Result of the aggregation operation
    """
    try:
        collection = get_collection(collection_name)
        
        # Execute aggregation pipeline
        cursor = collection.aggregate(pipeline)
        
        # Convert cursor to list with ObjectId conversion
        results = []
        for document in cursor:
            # Convert ObjectId to string if _id exists
            if "_id" in document and isinstance(document["_id"], pymongo.ObjectId):
                document["_id"] = str(document["_id"])
            results.append(document)
        
        logger.debug(f"Aggregation executed on {collection_name}, returned {len(results)} results")
        return results
    except errors.PyMongoError as e:
        logger.error(f"Error executing aggregation on {collection_name}: {str(e)}")
        raise


def close_connection() -> None:
    """
    Closes the MongoDB client connection.
    """
    global _mongo_client
    
    if _mongo_client is not None:
        logger.info("Closing MongoDB connection")
        _mongo_client.close()
        _mongo_client = None