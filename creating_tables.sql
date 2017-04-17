CREATE TABLE users (
  user_id INT PRIMARY KEY ,
  user_name text ,
  birth_date date ,
  password text
);

CREATE TABLE conversations (
  conversation_id INT PRIMARY KEY ,
  conversation_name text ,
  creator_id INT
);

CREATE TABLE user_conversation (
  user_id INTEGER REFERENCES users (user_id) ,
  coversation_id INTEGER REFERENCES conversations (conversation_id)
);

CREATE TABLE messages (
  message_id INT PRIMARY KEY ,
  content text ,
  sender_id INT ,
  delivery_time TIMESTAMP
);

CREATE TABLE conversation_message (
  message_id INT REFERENCES messages (message_id) ,
  conversation_id INT REFERENCES conversations (conversation_id)
);

CREATE TABLE attachments (
  attachment_id INT PRIMARY KEY ,
  message_id INT REFERENCES messages (message_id),
  file UUID--some tipe of data
);

