# Database Chatbot
A sophisticated PostgreSQL database chatbot powered by GPT-4 that enables natural language querying of database content. This project demonstrates my expertise in:

## Key Features
- **Natural Language Processing**: Converts plain English questions into precise SQL queries using OpenAI's GPT-4
- **Database Integration**: Robust PostgreSQL connection and query execution with proper security measures
- **Input Validation**: Implements thorough validation and SQL injection prevention
- **Conversation History**: Maintains chat logs with timestamps for audit trails
- **Modular Architecture**: Well-organized codebase with separate utilities for database operations, API calls, and system prompts

## Technical Stack
- Python
- PostgreSQL
- OpenAI GPT-4 API
- Streamlit (for the web interface)
- psycopg2 (PostgreSQL adapter)

## Architecture
The application follows clean code principles with modular components:
- `utils/db_funs.py`: Database connection and schema management
- `utils/system_prompts.py`: AI system prompts and table metadata handling
- `utils/fun_calling.py`: Function definitions for AI interactions
- `utils/helper_funs.py`: Utility functions for conversation logging
- `utils/config.py`: Configuration management and environment variables

## Security Features
- Secure database credentials management
- API key protection
- SQL injection prevention
- Rate limiting for API calls
- Input sanitization

## Future Enhancements
- Multi-database support
- Advanced query optimization
- User authentication system
- Enhanced error handling
- Query result visualization

This project showcases my ability to integrate AI capabilities with database systems while maintaining security best practices and clean code architecture.
