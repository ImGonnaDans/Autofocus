
// 方差锐度
double Squared_Grad(Mat img)
{
	double Squared = 0;;
	for (int i = 0; i < img.rows - 1; i++)
	{
		unsigned short* Prow = img.ptr<unsigned  short>(i);
		unsigned short* Prow_next = img.ptr<unsigned  short>(i + 1);
		for (int j = 0; j < img.cols; j++)
		{
			Squared += pow((double)abs(Prow[j] - Prow_next[j]), 2) + pow((double)abs(Prow[j] - Prow[j + 1]), 2);
		}
	}
	return Squared;
}

// TenenGrad
double Tenen_grad(Mat img)
{
	Mat imgSobel, imgSobel_x, imgSobel_y;
    Rect ROI = Rect(106, 136, 360, 300);
    img = img(ROI);
    //imshow("asd", ImageToBuffer(ROI));
    //waitKey(10);
	//medianBlur(img, img, 5);
    filter2D(img, img,CV_32F, Mat::ones(5,5,CV_16UC1));
    Sobel(img, imgSobel_x, CV_16UC1, 1, 0);
    Sobel(img, imgSobel_y, CV_16UC1, 0, 1);
    imgSobel = imgSobel_x + imgSobel_y;
    imgSobel.convertTo(imgSobel, CV_32FC1);
    pow(imgSobel, double(2), imgSobel);
	//图像的平均灰度
	double meanValue = 0.0;
	meanValue = sum(imgSobel)[0];
    //cout << meanValue << endl;
	return meanValue;
}

// BrenerGrad
double Brenner_grad(Mat img)
{
    Rect ROI = Rect(216, 176, 200, 160);
    img = img(ROI);
    medianBlur(img, img, 5);
	double Squared = 0;;
	for (int i = 0; i < img.rows - 2; i++)
	{
		unsigned short* Prow = img.ptr<unsigned  short>(i);
		for (int j = 0; j < img.cols; j++)
		{
			Squared += pow((double)(Prow[j + 2] - Prow[j]), 2);
		}
	}
	return Squared;
}

// 拉普拉斯锐度
float Laplacin_grad(Mat img)
{
	Mat imageSobel;
	Mat Filtered;
	medianBlur(img, Filtered, 3);
	Laplacian(Filtered, imageSobel, CV_16UC1, 1, 1);

	//图像的平均灰度
	double meanValue = 0.0;
	meanValue = mean(imageSobel)[0];

    SaveImagePro();

	return meanValue;
}

// 差分锐度
float Variance_function(Mat img)
{
	float meanValue = mean(img)[0];
	double Variance = 0;;
	for (int i = 0; i < img.rows; i++)
	{
		unsigned short* Prow = img.ptr<unsigned  short>(i);
		for (int j = 0; j < img.cols; j++)
		{
			Variance += pow((double)abs(Prow[j] - meanValue), 2);
		}
	}
	return Variance;
}

// 变频锐度
float freShifting_grad(Mat img, int freq)
{
    Rect selectRect = Rect(216, 176, 200, 160);
    Mat selectImg = img(selectRect);
	Mat imgC, imgD, imgR;
	float freShifting_grad = 0;
	for (int i = 0; i < selectImg.cols - freq * 2; i++)
	{
		for (int j = 0; j < selectImg.rows - freq * 2; j++)
		{
			Rect ROI = Rect(i, j, freq, freq);
			//imgC = rectangle(img, Point(i, j), Point(i + freq, j + freq), Scalar(0),1,0,0);
			imgC = selectImg(ROI);
			ROI = Rect(i + freq, j, freq, freq);
			imgR = selectImg(ROI);
			ROI = Rect(i, j + freq, freq, freq);
			imgD = selectImg(ROI);
			freShifting_grad += abs(mean(imgC)[0] - mean(imgD)[0]) + abs(mean(imgC)[0] - mean(imgR)[0]);
            
		}
	}
    //SaveImagePro();
    return freShifting_grad;
}


// 动量自动对焦
void autofocus_momentum()
{
    QueryPerformanceCounter(&BeginFocusTime);
    int i = 0;
    int FOCUS_STEP = 40, aa = 400, mm = 400;
    double LastLastSharp, LastSharp, NowSharp, LastMomentum, NowMomentum, step, acc = 0;
    // 找一个方向
    int FocusDirection = rand()>16384 ? 1 : -1;

    // 测一次，走一次
    //NowSharp = freShifting_grad(ImageFromBuffer, 8);
    NowSharp = Tenen_grad(ImageFromBuffer);
    double First = NowSharp;
    pGlobalContext->ComSendMessage(int(20)*FocusDirection);
    cout << ++i <<endl;
    Sleep(300);

    // 测二次，走二次，得动量1
    LastSharp = NowSharp;
    //NowSharp = freShifting_grad(ImageFromBuffer, 8);
    NowSharp = Tenen_grad(ImageFromBuffer);
    NowMomentum = (NowSharp - LastSharp)/LastSharp;

    // 若锐度减小则切换方向
    if (NowSharp<LastSharp)
        FocusDirection = -FocusDirection;
    do // 测n次，走n次，得加速度acc
    {
        step = FOCUS_STEP + NowMomentum * mm + acc * aa;
        step = step > 3*FOCUS_STEP ? 2*FOCUS_STEP : step;
        pGlobalContext->ComSendMessage(int(step)*FocusDirection);
        cout << ++i << "\t" << step << "\t" << NowMomentum << "\t" << acc << "\t" << NowSharp <<endl;
        Sleep(200);

        LastLastSharp = LastSharp;
        LastSharp = NowSharp;
        //NowSharp = freShifting_grad(ImageFromBuffer, 8);
        NowSharp = Tenen_grad(ImageFromBuffer);
        LastMomentum = (LastSharp - LastLastSharp)/LastLastSharp;
        NowMomentum = (NowSharp - LastSharp)/LastSharp;
        acc = NowMomentum - LastMomentum;

    }while(NowSharp > LastSharp);

    FocusDirection = - FocusDirection;
    //NowSharp = freShifting_grad(ImageFromBuffer, 8);
    NowSharp = Tenen_grad(ImageFromBuffer);
    do
    {
        pGlobalContext->ComSendMessage(int(10)*FocusDirection);
        cout << ++i << "\t" << NowSharp <<endl;
        Sleep(100);
        LastSharp = NowSharp;
        //NowSharp = freShifting_grad(ImageFromBuffer, 8);
        NowSharp = Tenen_grad(ImageFromBuffer);
    }while(NowSharp> LastSharp);
    double End = NowSharp;
    QueryPerformanceCounter(&StopFocusTime);
    cout << "time: " << ((StopFocusTime.QuadPart - BeginFocusTime.QuadPart)/cpuFreq.QuadPart) << endl;
    cout << "First/End: " << First << "/" << End << "/" << float(End-First)/First << endl << endl;
}