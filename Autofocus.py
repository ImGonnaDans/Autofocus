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