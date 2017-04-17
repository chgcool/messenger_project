CREATE TABLE users (
  user_id INT PRIMARY KEY ,
  user_name text NOT NULL,
  birth_date date ,
  password text
);

CREATE TABLE conversations (
  conversation_id INT PRIMARY KEY ,
  conversation_name text UNIQUE NOT NULL,
  creator_id INT
);

CREATE TABLE user_conversation (
  user_id INT REFERENCES users (user_id) NOT NULL,
  coversation_id INT REFERENCES conversations (conversation_id) NOT NULL,
  UNIQUE (user_id, coversation_id)
);

CREATE TABLE messages (
  message_id INT PRIMARY KEY ,
  content text ,
  sender_id INT ,
  delivery_time TIMESTAMP
);

CREATE TABLE conversation_message (
  message_id INT REFERENCES messages (message_id) NOT NULL,
  conversation_id INT REFERENCES conversations (conversation_id) NOT NULL,
  UNIQUE (message_id, conversation_id)
);

CREATE TABLE attachments (
  attachment_id INT PRIMARY KEY ,
  message_id INT REFERENCES messages (message_id) UNIQUE NOT NULL,
  file UUID--some type of data
);
