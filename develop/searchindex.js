Search.setIndex({docnames:["development","doc","index","install","licence"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["development.rst","doc.rst","index.rst","install.rst","licence.rst"],objects:{"admin.control":[[1,0,1,"","delete_user"]],"admin.login":[[1,1,1,"","NotAuthenticatedException"],[1,0,1,"","get_admin_user_data"],[1,0,1,"","login_token"],[1,0,1,"","logout"]],"admin.logs":[[1,0,1,"","get_logs"],[1,0,1,"","loguru_handler"]],"mod.config.config":[[1,2,1,"","AccessConfigError"],[1,2,1,"","BackupConfigError"],[1,2,1,"","ConfigHandler"],[1,2,1,"","CopyConfigError"],[1,2,1,"","NameConfigError"],[1,2,1,"","OperationConfigError"],[1,2,1,"","RebuildConfigError"]],"mod.config.config.ConfigHandler":[[1,3,1,"","__repr__"],[1,3,1,"","__str__"],[1,3,1,"","_backup_config_file"],[1,3,1,"","_copy_string"],[1,4,1,"","_directory"],[1,3,1,"","_rebuild_config"],[1,3,1,"","_search_config"],[1,3,1,"","_set_configparser"],[1,3,1,"","_validate"],[1,5,1,"","config_name"],[1,3,1,"","read"],[1,5,1,"","root_directory"],[1,3,1,"","write"]],"mod.config.validator":[[1,2,1,"","ConfigModel"]],"mod.config.validator.ConfigModel":[[1,2,1,"","Config"],[1,4,1,"","_abc_impl"],[1,4,1,"","debug"],[1,4,1,"","debug_expiration_date"],[1,4,1,"","error"],[1,4,1,"","expiration_date"],[1,4,1,"","folder"],[1,4,1,"","info"],[1,4,1,"","level"],[1,4,1,"","max_version"],[1,4,1,"","messages"],[1,4,1,"","min_version"],[1,4,1,"","secret_key"],[1,4,1,"","size_auth_id"],[1,4,1,"","size_password"],[1,4,1,"","uri"],[1,4,1,"","users"],[1,4,1,"","uvicorn_logging_disable"]],"mod.config.validator.ConfigModel.Config":[[1,4,1,"","anystr_strip_whitespace"]],"mod.controller":[[1,2,1,"","MainHandler"]],"mod.controller.MainHandler":[[1,3,1,"","_matrix_handler"],[1,3,1,"","_mtp_handler"],[1,3,1,"","get_response"]],"mod.db.dbhandler":[[1,2,1,"","DBHandler"]],"mod.db.dbhandler.DBHandler":[[1,3,1,"","__read_db"],[1,3,1,"","__repr__"],[1,3,1,"","__search_db_in_models"],[1,3,1,"","__str__"],[1,3,1,"","__write_db"],[1,4,1,"","_logger"],[1,4,1,"","_loglevel"],[1,3,1,"","add_admin"],[1,3,1,"","add_flow"],[1,3,1,"","add_message"],[1,3,1,"","add_user"],[1,3,1,"","create_table"],[1,5,1,"","debug"],[1,3,1,"","delete_table"],[1,3,1,"","get_admin_by_name"],[1,3,1,"","get_all_admin"],[1,3,1,"","get_all_flow"],[1,3,1,"","get_all_message"],[1,3,1,"","get_all_user"],[1,3,1,"","get_flow_by_exact_time"],[1,3,1,"","get_flow_by_less_time"],[1,3,1,"","get_flow_by_more_time"],[1,3,1,"","get_flow_by_title"],[1,3,1,"","get_flow_by_uuid"],[1,3,1,"","get_message_by_exact_time"],[1,3,1,"","get_message_by_exact_time_and_flow"],[1,3,1,"","get_message_by_less_time"],[1,3,1,"","get_message_by_less_time_and_flow"],[1,3,1,"","get_message_by_more_time"],[1,3,1,"","get_message_by_more_time_and_flow"],[1,3,1,"","get_message_by_text"],[1,3,1,"","get_message_by_uuid"],[1,3,1,"","get_table_count"],[1,3,1,"","get_user_by_login"],[1,3,1,"","get_user_by_login_and_password"],[1,3,1,"","get_user_by_uuid"],[1,3,1,"","update_flow"],[1,3,1,"","update_message"],[1,3,1,"","update_user"]],"mod.db.models":[[1,2,1,"","Admin"],[1,2,1,"","Flow"],[1,2,1,"","Message"],[1,2,1,"","UserConfig"]],"mod.error":[[1,2,1,"","ServerStatus"],[1,0,1,"","check_error_pattern"]],"mod.lib":[[1,2,1,"","Hash"]],"mod.lib.Hash":[[1,3,1,"","auth_id"],[1,3,1,"","check_password"],[1,5,1,"","get_key"],[1,5,1,"","get_salt"],[1,3,1,"","password_hash"]],"mod.logging":[[1,0,1,"","add_logging"]],"mod.protocol.matrix.worker":[[1,2,1,"","MatrixProtocol"]],"mod.protocol.matrix.worker.MatrixProtocol":[[1,3,1,"","get_response"]],"mod.protocol.mtp.api":[[1,2,1,"","Request"],[1,2,1,"","Response"]],"mod.protocol.mtp.api.Request":[[1,4,1,"","data"],[1,4,1,"","errors"],[1,4,1,"","jsonapi"],[1,4,1,"","meta"],[1,4,1,"","type"]],"mod.protocol.mtp.api.Response":[[1,4,1,"","data"],[1,4,1,"","errors"],[1,4,1,"","jsonapi"],[1,4,1,"","meta"],[1,4,1,"","type"]],"mod.protocol.mtp.worker":[[1,2,1,"","MTPErrorResponse"],[1,2,1,"","MTProtocol"]],"mod.protocol.mtp.worker.MTPErrorResponse":[[1,3,1,"","result"]],"mod.protocol.mtp.worker.MTProtocol":[[1,3,1,"","_add_flow"],[1,3,1,"","_all_flow"],[1,3,1,"","_all_messages"],[1,3,1,"","_authentication"],[1,3,1,"","_check_auth"],[1,3,1,"","_check_login"],[1,3,1,"","_check_protocol_version"],[1,3,1,"","_delete_message"],[1,3,1,"","_delete_user"],[1,3,1,"","_edited_message"],[1,3,1,"","_errors"],[1,3,1,"","_get_update"],[1,3,1,"","_ping_pong"],[1,3,1,"","_register_user"],[1,3,1,"","_send_message"],[1,3,1,"","_user_info"],[1,3,1,"","get_response"]]},objnames:{"0":["py","function","Python function"],"1":["py","exception","Python exception"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"],"5":["py","property","Python property"]},objtypes:{"0":"py:function","1":"py:exception","2":"py:class","3":"py:method","4":"py:attribute","5":"py:property"},terms:{"0":[3,4],"1":1,"10":[1,2],"15":1,"20":1,"2020":4,"2048":3,"25":1,"3":[0,2,3,4],"30":1,"40":1,"499":1,"5":[1,3],"50":1,"503":3,"505":1,"520":1,"526":1,"6455":2,"7692":2,"8":[0,3],"8000":3,"byte":1,"case":[1,3],"class":1,"default":[1,3],"do":3,"function":[0,1,3],"int":[1,3],"long":3,"new":[0,1,3],"public":[1,4],"return":1,"short":1,"static":[0,1],"switch":0,"true":1,"try":1,A:1,As:1,Be:0,By:1,For:[0,1],If:[0,1,3],In:3,Or:1,The:[1,3],To:[0,1,3],With:1,__name__:1,__read_db:1,__repr__:1,__search_db_in_model:1,__str__:1,__write_db:1,_abc:1,_abc_data:1,_abc_impl:1,_add_flow:1,_all_flow:1,_all_messag:1,_authent:1,_backup_config_fil:1,_check_auth:1,_check_login:1,_check_protocol_vers:1,_copy_str:1,_delete_messag:1,_delete_us:1,_directori:1,_edited_messag:1,_error:1,_get_upd:1,_logger:1,_loglevel:1,_matrix_handl:1,_mtp_handler:1,_ping_pong:1,_rebuild_config:1,_register_us:1,_search_config:1,_send_messag:1,_set_configpars:1,_user_info:1,_valid:1,about:[0,1,3],absenc:1,access:1,accessconfigerror:1,accord:[0,1],account:3,action:1,actual:1,ad:1,add:[0,1,3],add_admin:1,add_flow:[1,3],add_info:1,add_log:1,add_messag:1,add_us:1,addit:[2,3],addition:3,address:3,admin:[0,2],administr:[1,3],advanc:1,after:[1,3],against:1,ai:4,aliv:3,all:[0,1,3],all_flow:3,allow:[1,3],also:1,altern:2,alwai:3,an:[1,2,3],ani:1,anoth:1,answer:1,anystr_strip_whitespac:1,api:[0,1],app:3,appear:0,append:1,applic:[1,3],ar:[0,1,2,3],argument:[1,3],arrai:1,asgi2:3,asgi3:3,asgi:2,asterisk:0,asyncio:3,audio:1,auth:3,auth_id:[0,1],authent:1,author:[1,3],auto:[1,3],autom:1,automat:1,avail:3,avatar:1,backlog:3,backup:1,backupconfigerror:1,bak:1,basevers:1,basic:2,basicinterpol:1,becaus:1,befor:[1,2],behaviour:1,between:1,bio:1,blake2b:1,blank:1,blob:1,bool:1,branch:0,build:1,buildout:1,built:[0,2],c:4,ca:3,calcul:1,call:3,can:[1,3],catcher:1,cd:0,cert:3,certfil:3,certif:3,cfg:0,chang:[0,1],channel:1,chat:1,check:[0,1,3],check_error_pattern:1,check_password:1,checkout:0,choic:1,cipher:3,cli:3,click:0,client:[0,1,2],client_closed_request:1,clone:2,close:3,code:[1,2],collect:1,color:3,column:1,com:[0,1],command:[0,3],comment:0,commun:1,compar:0,comparison:1,compat:3,compil:3,complet:1,complianc:1,comput:0,concurr:3,config:[0,2,3],config_nam:1,confighandl:1,configmod:1,configmodel:1,configpars:1,configur:[0,1,2],connect:[1,3],consist:1,consol:[0,1,3],contain:[0,1],content:1,contribut:2,control:[0,2],convert:1,cooki:1,copi:[1,4],copyconfigerror:1,copyright:4,correct:1,correspond:1,could:1,count:0,coverag:0,creat:[1,2,3],create_t:1,critic:[1,3],current:2,custom:[0,1],data:[0,1,2,3],databas:[0,2,3],databaseaccesserror:1,databasereaderror:1,databasewriteerror:1,datarequest:1,datarespons:1,db:[0,1,3],dbhandler:[0,2],debug:[0,1,2],debug_expiration_d:1,debug_serv:[0,3],debug_statu:1,debugg:2,dedic:1,delet:[0,1,3],delete_t:1,delete_us:1,deni:3,depend:1,deploi:2,describ:[0,1],descript:[1,2],design:0,desir:1,desktop:[0,3],destin:1,detail:[1,4],detect:3,dict:[1,3],directori:[0,1,3],disabl:[1,3],discov:0,discuss:2,displai:[1,3],docstr:0,document:2,don:1,download:3,dst:1,duplic:1,dure:1,e:1,each:[0,1],easili:3,edited_statu:1,edited_tim:1,either:3,ellipsi:1,email:[1,3],embed:1,emoji:1,empti:3,enabl:[1,3],end:1,end_messag:3,ensur:3,enter:3,environ:[0,3],error:[0,2,3],error_messag:1,errorrespons:1,errorsrequest:1,errorsrespons:1,etc:1,even:3,event:3,everi:1,exampl:[0,1,3],example_config:[0,1],except:1,exist:1,expiration_d:1,extendedinterpol:1,fail:1,fals:1,fastapi:[1,2],favorit:1,featur:3,fetch:0,file:[0,1,3,4],file_audio:1,file_docu:1,file_pictur:1,file_video:1,find:1,first:[0,3],fixtur:[0,1],flag:1,flake8:0,floe:1,flow:[2,3],flow_count:1,flow_typ:1,flow_uuid:1,folder:1,follow:[0,1,2],fork:2,form:1,format:[1,3],found:1,framework:2,frequent:1,from:[0,1,3],full:1,fulli:1,g:1,gener:[0,1,4],get:[0,1],get_admin_by_nam:1,get_admin_user_data:1,get_all_admin:1,get_all_flow:1,get_all_messag:1,get_all_us:1,get_flow_by_exact_tim:1,get_flow_by_less_tim:1,get_flow_by_more_tim:1,get_flow_by_titl:1,get_flow_by_uuid:1,get_kei:1,get_log:1,get_message_by_exact_tim:1,get_message_by_exact_time_and_flow:1,get_message_by_less_tim:1,get_message_by_less_time_and_flow:1,get_message_by_more_tim:1,get_message_by_more_time_and_flow:1,get_message_by_text:1,get_message_by_uuid:1,get_on:1,get_respons:1,get_salt:1,get_table_count:1,get_upd:3,get_user_by_login:1,get_user_by_login_and_password:1,get_user_by_uuid:1,git:[2,3],github:[0,1,3],give:1,gnu:4,go:[0,3],googl:0,grant:1,greater:3,group:[1,2,3],gui:3,guid:0,h11:3,ha:1,half:1,hand:0,handl:1,handler:1,hash:[0,2],hash_password:1,have:[1,2],hazzari:4,header:1,heavi:3,help:[0,3],hi:1,high:1,higher:3,hold:3,home_pag:1,host:3,how:1,htmlrespons:1,http:[0,1,3],httpstatu:1,httptool:3,human:1,i:3,id:1,ident:1,identif:1,identifi:1,ignor:3,imag:1,impact:3,implement:[0,2,3],imposs:1,includ:1,incom:3,incorrect:1,index:2,info:[1,3],inform:[0,1,3],infrastructur:2,ini:[0,1],initi:1,ins:1,inspir:1,instal:2,instanc:1,instead:1,instruct:0,interact:[1,3],interfac:3,interpol:1,invalid:1,invalid_ssl_certif:1,irretriev:1,is_bot:1,issu:[1,2,3],issuanc:1,its:[0,1],itself:1,json:[0,1],jsonapi:1,just:0,keep:3,kei:[1,3],keyfil:3,known:3,kw:1,kwarg:1,lack:1,languag:2,last:1,later:4,latest:[0,1,3],launch:3,layer:1,lead:1,leak:3,led:1,lesser:4,level:[1,3],lgpl:4,lib:[0,1],librari:3,licens:2,lifespan:3,lightweight:2,like:1,limit:3,line:[0,1,3],link:[0,1],linter:0,list:[0,1],live:1,load:3,local:0,localhost:3,locat:1,log:[0,2,3],logger:1,login:[0,1],login_token:1,loginmanag:1,loglevel:1,logout:1,loguru_handl:1,loop:3,m:[0,3],ma1ex:4,made:3,mai:1,maiden:1,main:[0,1],mainhandl:2,maintain:2,make:[0,3],manag:[0,3],mani:1,master:[0,1],match:1,matrix:[0,2],matrixprotocol:2,max:3,max_vers:1,maximum:3,md:1,mean:1,memori:[1,3],menu:0,messag:[2,3],message_count:1,message_uuid:1,messeng:2,meta:1,method:[0,1],migrat:0,min_vers:1,mini:[0,3],minut:1,miss:1,mod:[0,1],mode:[0,2],model:[0,2],modul:[0,2,3],more:1,morelia:[0,2],morelia_protocol:1,morelia_serv:0,moreliatalk:[0,1],mother:1,mtp:[0,2],mtperrorrespons:2,mtpprotocol:1,mtprotocol:2,must:[0,3],name:[0,1],nameconfigerror:1,namedtupl:1,necessari:3,need:[0,3],nekrodnik:4,new_config:1,none:[1,3],nonetyp:1,notauthenticatedexcept:1,note:[1,3],number:[1,3],oauth2:1,oauth2passwordrequestform:1,object:[1,3],occur:1,occurr:0,off:[1,3],old:1,one:[1,3],onli:3,open:1,operationconfigerror:1,opm:0,option:[1,3],org:1,orig_config:1,origin:[0,1],orm:[1,2],other:1,out:1,output:[0,1],over:3,owner:1,packag:3,page:[0,1,2],panel:1,param:1,paramet:[1,3],pars:1,pass:[1,3],password:[0,1],password_hash:1,path:[0,1,3],path_to_model:1,pathlib:1,pattern:3,pdb:0,peopl:2,pep:0,perform:[0,1,3],permiss:1,person:1,photo:1,phrase:1,pictur:1,pip:3,pipenv:[0,2],pipfil:3,point:1,pool:2,port:3,possibl:[1,3],preliminarili:0,prepar:0,preprocess:1,prescrib:1,presenc:1,present:4,press:2,prevent:3,previou:1,previous:1,print:1,problem:1,process:[0,1,3],program:2,project:[0,1,2,3],properti:1,protocol:[0,2,3],provid:[1,3],pull:0,purepath:1,purpos:3,push:0,py:[0,1,3],pydant:[1,2],pylint:0,pypi:3,python:[0,2,3],quantiti:1,queri:[0,1,3],rais:1,raw:1,read:[0,1],readi:3,readm:1,reason:1,rebuild:1,rebuildconfigerror:1,receiv:[1,3],recogn:1,recommend:0,record:3,redirect:1,regist:1,relev:3,reload:3,remot:0,renam:0,replac:0,report:1,repositori:2,req:3,request:[2,3],requir:[1,2,3],resourc:3,respond:1,respons:[0,2,3],restor:1,result:1,retriev:1,rfc:2,right:[0,1],role:1,root:1,root_directori:1,row:1,ru:4,run:2,s:[0,1,3],salt:1,same:1,save:[0,1],scheme:1,search:[1,2],secret:1,secret_kei:1,section:1,secur:1,see:[3,4],select:[0,1,3],selectresult:1,send:[0,1,3],send_messag:3,sent:3,server:0,serverstatu:1,servic:3,session:1,set:[0,1,3],setup:0,sever:1,shell:3,show:[0,1],similar:0,simpl:1,size_auth_id:1,size_password:1,skriabin:4,slack:2,so:3,some:3,sourc:[0,1],spec:1,special:1,specif:1,sql:1,sqlite:1,sqlobject:[1,2],src:1,sresult:1,ssl:3,stabl:[0,1],stage:1,standard:1,starlett:[1,2],start:[0,1,2],startup:2,statist:0,statu:1,stderr:1,stdlib:3,stdout:1,step:0,stepan:4,str:[1,3],string:1,strip:1,style:2,subject:1,success:1,sum:0,superus:3,support:[1,3],sure:0,synchron:0,t:1,tabl:[0,1,3],take:3,task:3,team:0,telegram:2,templat:0,termin:3,test:[1,2,3],test_:0,text:1,than:1,them:1,thi:[1,3],thread:1,three:1,through:[0,1],time:1,time_cr:1,timeout:3,titl:1,togeth:3,token:1,token_ttl:1,trace:[1,3],traffic:3,trail:1,transmit:1,tupl:1,turn:1,two:[0,1,3],type:[0,1,3],under:[3,4],union:1,uniqu:1,unittest:0,univers:1,unix:1,unknown:1,unknown_error:1,unrecogn:1,up:3,updat:1,update_flow:1,update_messag:1,update_us:1,uppercas:1,uppermost:1,upstream:0,uri:[1,3],url:1,us:[0,1,3],usag:3,user:[1,3],user_count:1,user_uuid:1,userconfig:2,usernam:[0,1,3],util:[0,3],uuid:1,uvicorn:[1,3],uvicorn_logging_dis:1,uvloop:3,v1:1,v:0,valid:[0,2],valu:1,variant:1,verifi:1,version:[1,3,4],version_not_support:1,video:1,virtual:3,virtualenv:3,wa:1,wai:2,want:[0,3],warn:[0,1,3],we:1,web:1,websocket:[1,2,3],websocket_endpoint:1,well:0,when:[1,3],where:[0,1,2],whether:[1,3],which:[0,1,3],whitespac:1,who:1,window:3,within:3,without:1,work:[0,1,2],worker:[0,1],wrapper:0,write:[1,2],writer:1,written:1,ws:3,wsgi:3,wsproto:3,ximranx:4,you:[0,1,3],your:[0,3],yourself:0,zc:1},titles:["Development","Documentation","MoreliaTalk server","Install and Run","License"],titleterms:{For:2,addit:1,admin:1,befor:[0,3],built:3,client:3,clone:0,code:[0,4],config:1,configur:3,contact:2,content:2,contribut:4,control:1,creat:0,current:4,databas:1,dbhandler:1,debug:3,debugg:0,descript:0,develop:[0,2],document:1,error:1,flow:1,follow:4,fork:0,git:0,hash:1,have:4,indic:2,instal:3,licens:4,log:1,mainhandl:1,maintain:4,matrix:1,matrixprotocol:1,messag:1,mode:3,model:1,modul:1,morelia:4,moreliatalk:2,mtp:1,mtperrorrespons:1,mtprotocol:1,peopl:4,pipenv:3,pool:0,protocol:1,repositori:0,request:[0,1],requir:0,respons:1,run:[0,3],server:[1,2,3,4],start:3,startup:3,style:0,tabl:2,test:0,us:2,userconfig:1,valid:1,we:2,work:3,write:0}})