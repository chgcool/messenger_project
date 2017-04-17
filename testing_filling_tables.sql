insert into users (user_id, user_name, birth_date, password) values
-> ('1', 'Sergey Popov', '12.05.1956','SP56')
-> ('2', 'Ivan Petrov', '14.03.1989', 'IP39')
-> ('3', 'Roman Kuznezov', '17.05.1998', 'RK58')
-> ('4', 'Timur Budovskiy', '23.09.1997', 'TB97')
-> ('5', 'Matvey Romanov', '10.07.1996', 'MR76')
-> ('6', 'Igor Belov', '15.05.1974', 'IB54')
-> ('7', 'Egor Teterev', '04.03.1995', 'ET35')
-> ('8', 'Marie Walley', '17.05.1956', 'MR56')
-> ('9', 'Julie Smith', '11.08.1998', 'JS88')
-> ('10', 'Jane Johnson', '18.03.1998', 'JJ38');

insert into conversations (conversation_id, conversation_name, creator_id) VALUES
-> ('01', 'Party', '3')
-> ('02', 'Gift for Jane', '5')
-> ('03', 'Volleyball club', '7')
-> ('04', 'Dance classes', '10')
-> ('05', 'Jumping park', '4')
-> ('06', 'Computer science', '6')
-> ('07', 'English', '7')
-> ('08', 'Work out', '2')
-> ('09', 'Project', '5')
-> ('010', 'Hockey club', '8');

insert into user_conversation (user_id, conversation_id) values
-> ('1', '01')
-> ('2', '01')
-> ('3', '01')
-> ('4', '01')
-> ('5', '01');

