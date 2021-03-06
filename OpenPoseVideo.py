import cv2
import time
import numpy as np
import pandas as pd
import os
import math

MODE = "BODY25"
input_source = "demo1.mp4"
# demo1.mp4
# demo2.mp4

output_destination ='./destination/' + input_source.split('.')[0] + '.avi'
OUTPUT_CSV = './destination/Air Squat with Chris Spealler.mp4.csv'
FRAMES_TO_TAKE = 3

if MODE is "COCO":
    protoFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18
    POSE_PAIRS = [[1, 0], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12],
                  [12, 13], [0, 14], [0, 15], [14, 16], [15, 17]]

elif MODE is "MPI":
    protoFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
    weightsFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/mpi/pose_iter_160000.caffemodel"
    nPoints = 15
    POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 14], [14, 8], [8, 9], [9, 10], [14, 11],
                  [11, 12], [12, 13]]

elif MODE is "BODY25":
    protoFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/body_25/pose_deploy.prototxt"
    weightsFile = "C:/Users/romanrosh/openpose-1.4.0-win64-gpu-binaries/models/pose/body_25/pose_iter_584000.caffemodel"
    nPoints = 25
    POSE_PAIRS = [[1, 0], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12],
                  [12, 13], [0, 14], [0, 15], [14, 16], [15, 17],
                  [10, 11], [8, 12], [12, 13], [13, 14], [1, 0], [0, 15], [0, 16], [16, 18], [2, 17], [5, 18], [14, 19],
                  [19, 20], [14, 21], [11, 22], [22, 23], [11, 24]]

    BODY_25_COLUMNS = ["0-XNose",       "0-YNose",
                       "1-XNeck",       "1-YNeck",
                       "2-XRShoulder",  "2-YRShoulder",
                       "3-XRElbow",     "3-YRElbow",
                       "4-XRWrist",     "4-YRWrist",
                       "5-XLShoulder",  "5-YLShoulder",
                       "6-XLElbow",     "6-YLElbow",
                       "7-XLWrist",     "7-YLWrist",
                       "8-XMidHip",     "8-YMidHip",
                       "9-XRHip",       "9-YRHip",
                       "10-XRKnee",     "10-YRKnee",
                       "11-XRAnkle",    "11-YRAnkle",
                       "12-XLHip",      "12-YLHip",
                       "13-XLKnee",     "13-YLKnee",
                       "14-XLAnkle",    "14-YLAnkle",
                       "15-XREye",      "15-YREye",
                       "16-XLEye",      "16-YLEye",
                       "17-XREar",      "17-YREar",
                       "18-XLEar",      "18-YLEar",
                       "19-XLBigToe",   "19-YLBigToe",
                       "20-XLSmallToe", "20-YLSmallToe",
                       "21-XLHeel",     "21-YLHeel",
                       "22-XRBigToe",   "22-YRBigToe",
                       "23-XRSmallToe", "23-YRSmallToe",
                       "24-XRHeel",     "24-YRHeel"]

inWidth = 368
inHeight = 368
threshold = 0.1

cap = cv2.VideoCapture(input_source)
hasFrame, frame = cap.read()

vid_writer = cv2.VideoWriter(output_destination, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                             (frame.shape[1], frame.shape[0]))

net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
counter = 0
df_is_empty = True
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print('frames to retrieve', length)

while cv2.waitKey(1) < 0:
    if counter > length:
        break
    t = time.time()
    hasFrame, frame = cap.read()
    counter += 1
    if np.mod(counter, FRAMES_TO_TAKE) != 0:
        continue
    if counter < 25:
        continue
    print('frame', counter)
    frameCopy = np.copy(frame)
    if not hasFrame:
        cv2.waitKey()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]
    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        # Scale the point to fit on the original image
        x = (frameWidth * point[0]) / W
        y = (frameHeight * point[1]) / H

        if prob > threshold:
            cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1,  #change to 1
                        lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append((int(x), int(y)))
        else:
            points.append(None)
    flat_array = []
    for point in points:
        if point is None:
            flat_array.append(None)
            flat_array.append(None)
        else:
            for feature in point:
                flat_array.append(feature)
    flat_array = pd.Series(np.array(flat_array))
    # flat_array = np.array([feature for point in points for feature in point])
    if df_is_empty:
        df = pd.DataFrame([flat_array])
        df_is_empty = False
    else:
        df = df.append(flat_array, ignore_index=True)
    print('dataframe size', len(df))
    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 3)
            cv2.circle(frame, points[partA], 8, (0, 0, 255))
            cv2.circle(frame, points[partB], 8, (0, 0, 255))
        # print(points)
    # cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (50, 50), cv2.FONT_HERSHEY_COMPLEX, .8,
    #             (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.putText(frame, "OpenPose using OpenCV", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.imshow('Output-Keypoints', frameCopy)
    cv2.imshow('Output-Skeleton', frame)
    vid_writer.write(frame)
    if hasFrame == False:
        break
vid_writer.release()

df.columns = BODY_25_COLUMNS
df.fillna(value=pd.np.nan, inplace=True)

def nans_list(df):
    import math
    nans = []
    for i in np.arange(df.shape[0]):
        for j in np.arange(df.shape[1]):
            if math.isnan(df.iloc[i,j]):
                nans.append((i,j))
    return nans

nans = nans_list(df)
print(f"NaNs left to deal with: {len(nans)}")

## for points not at the edge, if NaN take the mean around them

persistent_nans = []
for point in nans:
    if point[0]>4 and point[0]<df.shape[0]-5:
        df.iloc[point[0], point[1]] = np.nanmean(df.iloc[point[0]-5:point[0]+6,point[1] ])

print(f"NaNs left to deal with at the edges: {len(nans_list(df))}")

print(nans_list(df))

reverse_top = np.arange(0,15)[::-1]

for row in reverse_top:
    for col in np.arange(df.shape[1]):
        print(row, col)
        if math.isnan(df.iloc[row, col]):
            df.iloc[row, col] = df.iloc[row+1, col]


for row in np.arange(df.shape[0]-10, df.shape[0]):
    for col in np.arange(df.shape[1]):
        if math.isnan(df.iloc[row, col]):
            df.iloc[row, col] = df.iloc[row-1, col]

print(f"NaNs left to deal with: {len(nans_list(df))}")



def anomaly_detector(arr):
    array_mean = np.mean(arr)
    array_std = np.std(arr)
    mid_point = arr.iloc[int((arr.shape[0]+1)/2 - 1)]
    if array_std>0 and np.abs(mid_point-array_mean)/array_std > 2:
#         print('anomaly handled')
        return array_mean, True
    return mid_point, False


iterations = 0
found_anomalies = True
while found_anomalies:
    iterations += 1
    found_anomalies = False
    for row in np.arange(5,df.shape[0]-5):
        for col in np.arange(df.shape[1]):
            result = anomaly_detector(df.iloc[row-5:row+6, col])
            df.iloc[row, col] = result[0]
            if result[1]:
                found_anomalies = True
print(f"{iterations} iterations required")

## anomalies on edges (top/bottom 5 rows)

def edge_anomaly_detector(arr, val):
    array_mean = np.mean(arr)
    array_std = np.std(arr)
    #     mid_point = arr.iloc[int((arr.shape[0]+1)/2 - 1)]
    if array_std > 0 and np.abs(val - array_mean) / array_std > 2:
        print('anomaly handled')
        return array_mean, True
    return val, False


iterations = 0
found_anomalies = True
while found_anomalies:
    iterations += 1
    found_anomalies = False
    for row in np.arange(5):
        for col in np.arange(df.shape[1]):
            result = edge_anomaly_detector(df.iloc[:5, col], df.iloc[row, col])
            df.iloc[row, col] = result[0]
            if result[1]:
                found_anomalies = True
    for row in np.arange(df.shape[0]):
        for col in np.arange(df.shape[1]):
            result = edge_anomaly_detector(df.iloc[df.shape[0]-5:, col], df.iloc[row, col])
            df.iloc[row, col] = result[0]
            if result[1]:
                found_anomalies = True
print(f"{iterations} iterations required")

print(df)

for i in range(len(df)):
    # RIGHT KNEE
    u = (df.loc[i, '9-XRHip'] - df.loc[i, '10-XRKnee'], df.loc[i, '9-YRHip'] - df.loc[i, '10-YRKnee'])
    v = (df.loc[i, '11-XRAnkle'] - df.loc[i, '10-XRKnee'], df.loc[i, '11-YRAnkle'] - df.loc[i, '10-YRKnee'])
    c = np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)
    df.loc[i, 'RightKneeAngle'] = np.arccos(np.clip(c, -1, 1)) * 180 / np.pi
    # LEFT KNEE
    u = (df.loc[i, '12-XLHip'] - df.loc[i, '13-XLKnee'], df.loc[i, '12-YLHip'] - df.loc[i, '13-YLKnee'])
    v = (df.loc[i, '14-XLAnkle'] - df.loc[i, '13-XLKnee'], df.loc[i, '14-YLAnkle'] - df.loc[i, '13-YLKnee'])
    c = np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)
    df.loc[i, 'LeftKneeAngle'] = np.arccos(np.clip(c, -1, 1)) * 180 / np.pi
    # heel ankle toe knee left side
    toes_x = (df.loc[i, "19-XLBigToe"] + df.loc[i, "20-XLSmallToe"]) / 2
    toes_y = (df.loc[i, "19-YLBigToe"] + df.loc[i, "20-YLSmallToe"]) / 2
    heel_angle_x = (df.loc[i, "21-XLHeel"] + df.loc[i, "14-XLAnkle"]) / 2
    heel_angle_y = (df.loc[i, "21-YLHeel"] + df.loc[i, "14-XLAnkle"]) / 2
    u = (toes_x - heel_angle_x, toes_y - heel_angle_y)
    v = (heel_angle_x - df.loc[i, '13-XLKnee'], heel_angle_y - df.loc[i, '13-YLKnee'])
    c = np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)
    df.loc[i, 'LeftHeelAngleAngle'] = np.arccos(np.clip(c, -1, 1)) * 180 / np.pi
    # heel ankle toe knee right side
    toes_x = (df.loc[i, "22-XRBigToe"] + df.loc[i, "23-XRSmallToe"]) / 2
    toes_y = (df.loc[i, "22-YRBigToe"] + df.loc[i, "23-YRSmallToe"]) / 2
    heel_angle_x = (df.loc[i, "24-XRHeel"] + df.loc[i, "11-XRAnkle"]) / 2
    heel_angle_y = (df.loc[i, "24-YRHeel"] + df.loc[i, "11-YRAnkle"]) / 2
    u = (toes_x - heel_angle_x, toes_y - heel_angle_y)
    v = (heel_angle_x - df.loc[i, '10-XRKnee'], heel_angle_y - df.loc[i, '10-YRKnee'])
    c = np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)
    df.loc[i, 'RightHeelAngleAngle'] = np.arccos(np.clip(c, -1, 1)) * 180 / np.pi
    # hip neck knee
    knee_x = (df.loc[i, "10-XRKnee"] + df.loc[i, "13-XLKnee"]) / 2
    knee_y = (df.loc[i, "10-YRKnee"] + df.loc[i, "13-YLKnee"]) / 2
    u = (knee_x - df.loc[i, '8-XMidHip'], knee_y - df.loc[i, '8-YMidHip'])
    v = (df.loc[i, '1-XNeck'] - df.loc[i, '8-XMidHip'], df.loc[i, '1-YNeck'] - df.loc[i, '8-YMidHip'])
    c = np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)
    df.loc[i, 'HipAngle'] = np.arccos(np.clip(c, -1, 1)) * 180 / np.pi

exists = os.path.isfile(OUTPUT_CSV)

if exists:
    with open(OUTPUT_CSV, 'a') as f:
        df.to_csv(f, header=False)
else:
    df.to_csv(OUTPUT_CSV)