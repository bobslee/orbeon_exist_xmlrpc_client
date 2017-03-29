"""
Exist XML-RPC API: http://exist-db.org/exist/apps/doc/devguide_xmlrpc.xml

Setup Orbeon/Exist XML-RPC Server
=================================

To enable access to the Orbeon/Exist XML-RPC server, uncomment following lines in a Orbeon config-file:

- File: <orbeon>/WEB-INF/web.xml
- Uncomment nodes:

  <servlet>
    <servlet-name>exist-xmlrpc-servlet</servlet-name>
    <servlet-class>org.exist.xmlrpc.RpcServlet</servlet-class>
  </servlet>-->

  <servlet-mapping>
    <servlet-name>exist-xmlrpc-servlet</servlet-name>
    <url-pattern>/exist/xmlrpc</url-pattern>
  </servlet-mapping>


Optional setup of Orbeon/Exist REST(HTTP) Server
================================================

To enable access to the Orbeon/Exist REST(HTTP) server, comment following lines in a Orbeon-config-file:

- File: <orbeon>/WEB-INF/web.xml
- Comment node:

  <filter-mapping>
    <filter-name>orbeon-exist-filter</filter-name>
    <url-pattern>/exist/*</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
  </filter-mapping>
"""

from lxml import etree

import argparse
import datetime
import logging
import xmlrpclib

FORMAT = "%(asctime)-15s %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(10)


class OrbeonExistXMLRPC(object):

    def __init__(self, orbeon_uri, collection_path, output_filename):
        """
        orbeon_address e.g: 'http://localhost:8080/orbeon'
        """
        logger.debug('orbeon_uri: %s' % orbeon_uri)
        logger.debug('collection_path: %s' % collection_path)
        logger.debug('output_filename: %s' % output_filename)

        self.orbeon_uri = orbeon_uri
        self.collection_path = collection_path
        self.output_filename = output_filename

        self.collection_database_path = None
        self.set_collection_database_path()

        self.exist_uri = orbeon_uri + '/exist/xmlrpc'
        logger.debug('exist uri: %s' % self.exist_uri)

        self.server = xmlrpclib.ServerProxy(self.exist_uri)

        # logger.debug('collection_path: %s' % self.collection_path)
        logger.debug('collection: %s' % self.server.describeCollection(self.collection_database_path))

    def set_collection_database_path(self):
        path = ['/db', 'orbeon', 'fr']
        path.append(self.collection_path)
        self.collection_database_path = '/'.join(path)

    def load_data_collections(self):
        res = self.server.describeCollection(self.collection_database_path)
        root = etree.Element("data")

        with open(self.output_filename, 'ab') as text_file:

            for c in res['collections']:
                path = "%s/%s" % (self.collection_database_path, c)
                collection = self.server.describeCollection(path)
                data_path = '/'.join([path, 'data.xml'])
                doc = self.server.getDocumentAsString(data_path, {'encoding': 'UTF-8'})

                doc_root = etree.fromstring(doc)
                created = etree.Element("created")
                created.text = datetime.datetime.fromtimestamp(int(collection['created'])/1000.0).strftime('%d-%m-%Y')

                doc_root.append(created)
                root.append(doc_root)

            text_file.write('%s' % etree.tostring(root, pretty_print=True).encode('utf-8'))


parser = argparse.ArgumentParser(description="Get data from an (Orbeon) Exist-db via XML-RPC")
parser.add_argument('-u', '--uri', help='(Orbeon) URI e.g. "http://localhost:8080/orbeon"', required=True)
parser.add_argument('-c', '--collection_path', help='Collection-path e.g. "contactform/2017/data"', required=True)
parser.add_argument('-o', '--output_filename', help='Output (XML) filename"', required=True)

args = parser.parse_args()

xmlrpc = OrbeonExistXMLRPC(args.uri, args.collection_path, args.output_filename)
xmlrpc.load_data_collections()
