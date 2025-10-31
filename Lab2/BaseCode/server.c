
/*
fragmenty kodu dla serwera WWW
opracowano na podstawie dostepnych przykladow
*/

void displayOwnIp(void)
{

  xprintf(
    "My IP: %d.%d.%d.%d\n",
    ip4_addr1_16(netif_ip4_addr(&gnetif)),
    ip4_addr2_16(netif_ip4_addr(&gnetif)),
    ip4_addr3_16(netif_ip4_addr(&gnetif)),
    ip4_addr4_16(netif_ip4_addr(&gnetif))
    );
}

static char response[500];

//based on available code examples
static void http_server_serve(struct netconn *conn)
{
  struct netbuf *inbuf;
  err_t recv_err;
  char* buf;
  u16_t buflen;

  /* Read the data from the port, blocking if nothing yet there.
   We assume the request (the part we care about) is in one netbuf */
  recv_err = netconn_recv(conn, &inbuf);

  if (recv_err == ERR_OK)
  {
    if (netconn_err(conn) == ERR_OK)
    {
      netbuf_data(inbuf, (void**)&buf, &buflen);

      /* Is this an HTTP GET command? (only check the first 5 chars, since
      there are other formats for GET, and we're keeping it very simple )*/
      if ((buflen >=5) && (strncmp(buf, "GET /", 5) == 0))
      {
        response[0] = 0;

        strcpy(response, "HTTP/1.1 200 OK\r\n\
          Content-Type: text/html\r\n\
          Connnection: close\r\n\r\n\
          <!DOCTYPE HTML>\r\n");

        strcat(response,"<title>Prosta strona WWW</title>");
        strcat(response,"<h1>H1 Header</h1>");

        strcat(response,"A to jest tekst na stronie");
          netconn_write(conn, response, sizeof(response), NETCONN_NOCOPY);
      }
    }
  }
  /* Close the connection (server closes in HTTP) */
  netconn_close(conn);

  /* Delete the buffer (netconn_recv gives us ownership,
   so we have to make sure to deallocate the buffer) */
  netbuf_delete(inbuf);
}


//based on available code examples
static void http_server_netconn_thread(void const *arg)
{
  struct netconn *conn, *newconn;
  err_t err, accept_err;

  xprintf("http_server_netconn_thread\n");

  /* Create a new TCP connection handle */
  conn = netconn_new(NETCONN_TCP);

  if (conn!= NULL)
  {
    /* Bind to port 80 (HTTP) with default IP address */
    err = netconn_bind(conn, NULL, 80);

    if (err == ERR_OK)
    {
      /* Put the connection into LISTEN state */
      netconn_listen(conn);

      while(1)
      {
        /* accept any icoming connection */
        accept_err = netconn_accept(conn, &newconn);
        if(accept_err == ERR_OK)
        {
          /* serve connection */
          http_server_serve(newconn);

          /* delete connection */
          netconn_delete(newconn);
        }
      }
    }
  }
}

