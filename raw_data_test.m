% 1 is thigh 2 is shin 
rep = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output';
cd(rep)
sensor1 = table2array(readtable('extension_test1_sensor1.csv'));
sensor2 = table2array(readtable('extension_test1_sensor2.csv'));

%% average / calibrate
n = find(sensor2(:,1) <= 20); 
avg1 = mean(sensor1(n,2:4)); 
avg2 = mean(sensor2(n,2:4)); 

sensor1(:,2:4) = sensor1(:,2:4) - avg1;
sensor2(:,2:4) = sensor2(:,2:4) - avg2;

%% plot
close all
plot(sensor1(:,1),sensor1(:,2),'k')
hold on
plot(sensor1(:,1),sensor1(:,3),'b')
hold on
plot(sensor1(:,1),sensor1(:,4),'g')
hold on

figure
plot(sensor1(:,1),sensor1(:,2),'k')
hold on

plot(sensor2(:,1),sensor2(:,2),'r')
title('x')
simin=sensor1(:,2);
figure
plot(sensor1(:,1),sensor1(:,3),'k')
hold on
plot(sensor2(:,1),sensor2(:,3),'r')
title('y')

figure
plot(sensor1(:,1),sensor1(:,4),'k')
hold on
plot(sensor2(:,1),sensor2(:,4),'r')
title('z')

Y = fft(simin); 
L = max(sensor1(:,1)); 
Fs = 1000;

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs*(0:(L/2))/L;
figure
plot(f,P1) 