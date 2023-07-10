#!/usr/bin/python3
#This Script is used to deploy certbot generated certificates to specific directories
import os
import os.path
import logging
import json
import argparse, sys
import shutil


#Check if a given file exist - if not return false
def file_exist(path):
    if(path is None):
        logging.warn("No path  provided!")
        return False
    else:
        path_exist = os.path.exists(path)
        path_is_file = os.path.isfile(path)

        if(path_exist and path_is_file):
            return True
        else:
            return False

#load the config from a given path and return the JSON file as dict
def load_config(path):
    if(not file_exist(path)):
        logging.error("The given path " + path + " does not exist! - Please provide a valid config path")
        return False
    else:
        try:
            config_file = open(path)
            config_data = json.load(config_file)
            config_file.close()

            if(not config_data == False):
                logging.debug("Config successfully loaded")
                return config_data
            else:
                logging.error("Error while loading the config!")
                return False
        except:
            logging.error("Error while loading the config!")

#for correct handling the domain of the certificate deploy hook is spliced in its dissolved form.
#These Data will be returned and from there on these data will be used to match all needed rules
def format_domain(certificate_domain):
    try:
        domain_data = {}
        domain_parts = certificate_domain.split(".")
        domain_has_third_level = True
        #check if there are enough parts in this domain to be a realistic domain (only a .com is not useable as domain at least first-level.domain is needed)
        if(len(domain_parts) < 2):
            print("Len is: " + len(domain_parts))
            logging.warning("There are not enough parts to form a valid certificate useable domain!")
            return False

        domain_tld = domain_parts[len(domain_parts)-1]
        domain_name = domain_parts[len(domain_parts)-2]

        #all subdomain levels are stored here
        sub_domain = []
        
        if(len(domain_parts) > 2):
            del domain_parts[-2:]
            for domain_part in reversed(domain_parts):
                sub_domain.append(domain_part)
        else:
            domain_has_third_level = False

        #Even this is technically not correct the domainname is in this case only 2nd Level and Top Level Domain
        domain_data["domain_name"] = domain_name + "." + domain_tld
        domain_data["domain_tld"] = domain_tld
        domain_data["domain_second_level"] = domain_name
        if(domain_has_third_level):
            domain_data["domain_sub_level"] = sub_domain[::-1][0]

        else:
            domain_data["domain_sub_level"] = False

        if domain_data["domain_name"] == None or domain_data["domain_name"] == "" or domain_data["domain_tld"] == None or domain_data["domain_tld"] == "" or domain_data["domain_second_level"] == None or domain_data["domain_second_level"] == "":
            logging.error("Error while formatting Domain! - There are missing Data in essentials parts of the Domain")
            return False

        return domain_data
    except Exception as e:
        logging.error("Error while splitting domain in parts! - Error: " + str(e))
        return False

def is_rule_matching(rule, domain_data):
    try:
        #check if domain is sub or base
        if not domain_data["domain_sub_level"]:
            #only base domain certificate
            if rule["base"]:
                #Rule is for plain domain (no wildcard, no sub)
                logging.debug("Rule for base domain can be applied on domain " + str(domain_data))
                return True
            else:
                #rule is not for plain
                logging.debug("Rule for base domain can NOT be applied on domain " + str(domain_data))
                return False
        else:
            #check if cert is wildcard
            if domain_data["domain_sub_level"] == "*":
                if rule["wildcard"]:
                    logging.debug("Rule for wildcard domain can be applied on domain " + str(domain_data))
                    return True
                else:
                    logging.debug("Rule for wildcard domain can NOT be applied on domain " + str(domain_data))
                    return False
            else:
                #check if subdomain is in domains for rule
                if domain_data["domain_sub_level"] in rule["domains"]:
                    logging.debug("Rule for subdomain can be applied on domain " + str(domain_data))
                    return True
                else:
                    logging.debug("Rule for subdomain domain can NOT be applied on domain " + str(domain_data) + " - rule does not match at all!")
                    return False
    except:
        logger.error("Error while deciding rule!")
        return False
def get_targets(domain_data):
    try:
        #config
        logger.debug("Try to find a matching rule for domain " + str(domain_data))
        avail_config = config[domain_data["domain_name"]]

        if avail_config:
            rule_found = False
            targets = []
            for rule in avail_config:
                rule_matches = is_rule_matching(rule, domain_data)

                if rule_matches:
                    rule_found = True
                    for target in rule["target"]:
                        targets.append(target)
            if rule_found:
                return targets
            else:
                return False
        else:
            return False
    except:
        logging.warning("Can't find matching rule for domain " + str(domain_data) + " check if that is right!")
        return False

def deploy_file(targets, src):
    try:
        for target in targets:
            #check if paths are existing and make them absolute
            if not os.path.isabs(src):
                src = os.path.abspath(src)
            if not os.path.isabs(target):
                target = os.path.abspath(target)

            #remove and \ cause it makes problems...
            if "\\" in target:
                target = str(target).replace("\\", "/")
            if "\\" in src:
                src = str(src).replace("\\", "/")
            if not os.path.exists(target):
                logging.info("Target directory does not exist - create...")
                os.mkdir(target, 777)

            if os.path.exists(target):
                if os.path.exists(src):
                    shutil.rmtree(target)
                    shutil.copytree(src, target, False)
                else:
                    logging.error("Cant find src (Certificates) from letsencrypt! - Provided Path: " + str(src))
            else:
                logging.error("Cant find destination! - try to create - Provided Path: " + str(target))
    except Exception as e:
        logging.error("Error while deploying Certificates! - SRC: " + str(src) + str(", Targets: ") + str(targets) + " E_MESSAGE: " + str(e))



#MAIN
parser=argparse.ArgumentParser(
    prog="certbot-deploy",
    description="This program is used to deploy multiple certificates based on a json config"
)
parser.add_argument("-config", help="Config File with all domains and targets (default=./config.json)", default="./config.json", required=False)

args=parser.parse_args()

#set logger and configure it
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='./test.log', filemode='w')


#Check if config File exist and is valid JSON
config = load_config(args.config)

logger.debug("-------------")
logger.debug(os.environ)
logger.debug("Var: ")
logger.debug(os.environ.get('RENEWED_LINEAGE'))
logger.debug("Var 2: ")
logger.debug(os.environ.get('RENEWED_DOMAINS'))

if not config:
    logging.error("Stop Script - Error while loading config!")
    exit(-1)
else:
    logging.debug("Config successfully loaded")
    logging.debug("Provided Data from Certbot: Domains Renewed: " + str(os.environ.get('RENEWED_DOMAINS')) + str(", Folder: " + str(os.environ.get('RENEWED_LINEAGE'))))
    #check for domains path (check if this folder exist)
    try:
        path_exist = os.path.exists(os.environ.get('RENEWED_LINEAGE'))
    except:
        logging.error("No env. var found!")
        exit()
    
    if(not path_exist):
        logging.error("Can't find renewed domains certificate folder! - Provided Folder: " + str(os.environ.get('RENEWED_LINEAGE')))
        exit(-1)
    else:
        certs_path = os.environ.get('RENEWED_LINEAGE')
        domains = os.environ.get('RENEWED_DOMAINS')
        domains = domains.split()
        #config
        #format_domain(domains[1])

        for renewed_domain in domains:
            domain_data = format_domain(renewed_domain)

            if domain_data == False:
                print("Error")
                logging.error("Exit Script - Error while formatting Domain!")
                exit(-1)
            else:
                logging.debug("Start to decide rule from config")
                deploy_paths = get_targets(domain_data)
                if not deploy_paths:
                    continue
                else:
                    deploy_file(deploy_paths, certs_path)
