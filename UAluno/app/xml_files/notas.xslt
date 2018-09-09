<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:choose>
            <xsl:when test=".//course">
                <table class="table table-striped table-hover ">
                    <thead>
                        <tr>
                            <th>Cadeira</th>
                            <th>Ect's</th>
                            <th>Ano</th>
                            <th>Semestre</th>
                            <th>Área</th>
                            <th>Nota</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <xsl:for-each select=".//course">
                            <xsl:sort select="@year"></xsl:sort>
                            <xsl:sort select="@semester"></xsl:sort>
                            <xsl:sort select="@name"></xsl:sort>

                            <tr class="active">
                                <td><xsl:value-of select="@name"></xsl:value-of></td>
                                <td><xsl:value-of select="@ects"></xsl:value-of></td>
                                <td><xsl:value-of select="@year"></xsl:value-of></td>
                                <td><xsl:value-of select="@semester"></xsl:value-of></td>
                                <td><xsl:value-of select="@area"></xsl:value-of></td>
                                <xsl:choose>
                                    <xsl:when test="grade &gt; 9">
                                        <td style="background-color:#18bc9c; color:white;"><xsl:value-of select="grade"></xsl:value-of></td>
                                    </xsl:when>
                                    <xsl:otherwise>
                                            <td style="background-color:#e74c3c; color:white;"><xsl:value-of select="grade"></xsl:value-of></td>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <td><button class="btn-sm btn-warning btnremove" value="{@name}">Remover</button></td>
                            </tr>
                        </xsl:for-each>
                    </tbody>

                </table>
                 <h4>Média: <b><xsl:value-of select="format-number(sum(.//course/grade) div count(.//course/grade), '#.00')"></xsl:value-of></b></h4>
            </xsl:when>
            <xsl:otherwise>
                <p>Não tens notas registadas. </p>
                <p>Podes registar clicando no botão Adicionar nota.</p>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>

</xsl:stylesheet>
