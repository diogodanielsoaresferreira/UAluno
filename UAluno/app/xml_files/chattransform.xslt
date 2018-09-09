<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:param name="uid" />

    <xsl:template match="/">
        <xsl:for-each select="chat/message">

            <xsl:choose>
                <xsl:when test="$uid=@id">
                    <div class="row msg_container base_sent">
                        <div class="col-md-10 col-xs-10 ">
                            <div class="messages msg_sent">
                                <p><xsl:value-of select="."/></p>
                                <time><xsl:value-of select="@name"/> • <xsl:value-of select="@timestamp"/></time>
                            </div>
                        </div>
                    </div>
                </xsl:when>
                <xsl:otherwise>
                    <div class="row msg_container base_receive">
                        <div class="col-md-10 col-xs-10 ">
                            <div class="messages msg_receive">
                                <p><xsl:value-of select="."/></p>
                                <time><xsl:value-of select="@name"/> • <xsl:value-of select="@timestamp"/></time>
                            </div>
                        </div>
                    </div>
                </xsl:otherwise>
            </xsl:choose>

        </xsl:for-each>


    </xsl:template>
</xsl:stylesheet>