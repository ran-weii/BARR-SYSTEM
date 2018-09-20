%% Analysis 
% This file is used to analyze raw IMU sensor readings
---------------------------------------------------------------------
%% load data from csv file 
% change file names and repositories for other csv files
% 1 is thigh 2 is shin 
rep = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output';
cd(rep);
% sensor1 = table2array(readtable('extension_test1_sensor1.csv'));
% sensor2 = table2array(readtable('extension_test1_sensor2.csv'));
sensor1 = table2array(readtable('walking_test_2_sensor1.csv'));
sensor2 = table2array(readtable('walking_test_2_sensor2.csv'));

%% average / calibrate
% use the first 20 seconds to offset data 
% n = find(sensor2(:,1) <= 20); 
% avg1 = mean(sensor1(n,2:4)); 
% avg2 = mean(sensor2(n,2:4)); 
% 
% sensor1(:,2:4) = sensor1(:,2:4) - avg1;
% sensor2(:,2:4) = sensor2(:,2:4) - avg2;

%% plot
figure(1) 
grid on;
plot(sensor1(:,1),sensor1(:,2),'k'); hold on
plot(sensor1(:,1),sensor1(:,3),'b'); hold on
plot(sensor1(:,1),sensor1(:,4),'g'); hold off
title('x-y-z'); xlabel('time'); ylabel('acceleration'); 
legend('x', 'y', 'z')

figure(2) 
grid on;
plot(sensor1(:,1),sensor1(:,2),'k'); hold on
plot(sensor1(:,1),sensor2(:,2),'r'); hold off 
title('x'); xlabel('time'); ylabel('acceleration'); 
legend('sensor 1', 'sensor 2'); 

figure(3) 
grid on;
scatter(sensor1(:,1),sensor1(:,3),'k'); hold on
scatter(sensor1(:,1),sensor2(:,3),'r'); hold off 
title('y'); xlabel('time'); ylabel('acceleration'); 
legend('sensor 1', 'sensor 2'); 

figure(4)
grid on;
plot(sensor1(:,1),sensor1(:,4),'k'); hold on
plot(sensor1(:,1),sensor2(:,4),'r'); hold off 
title('z'); xlabel('time'); ylabel('acceleration'); 
legend('sensor 1', 'sensor 2'); 

%% fast fourier transform 
% this is copied from matlab fft example 
% Y = fft(simin); 
% L = max(sensor1(:,1)); 
% Fs = 1000;
% 
% P2 = abs(Y/L);
% P1 = P2(1:L/2+1);
% P1(2:end-1) = 2*P1(2:end-1);
% f = Fs*(0:(L/2))/L;
% figure
% plot(f,P1) 
