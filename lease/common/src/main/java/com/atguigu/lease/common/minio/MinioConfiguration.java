package com.atguigu.lease.common.minio;

import io.minio.MinioClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
//@ConditionalOnProperty(name = "minio.endpoint")
@EnableConfigurationProperties(MinioProperties.class)
//@ConfigurationPropertiesScan("com.atguigu.lease.common.minio")
public class MinioConfiguration {

    @Autowired
    private MinioProperties Properties;

    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder().endpoint(Properties.getEndpoint()).credentials(Properties.getAccessKey(), Properties.getSecretKey()).build();

    }
}

