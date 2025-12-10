// MainActivity.kt (کد به روز شده و کامل)

package com.example.guidora

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.guidora.ui.LoginScreen // ⬅️ ایمپورت موجود
import com.example.guidora.ui.OTPScreen // ⬅️ ایمپورت موجود
import com.example.guidora.ui.RoleScreen // 🆕 ایمپورت جدید برای RoleScreen
import com.example.guidora.ui.theme.GuidoraTheme

// =================================================================
// تنظیمات ثابت (آدرس ها و رنگ)
// =================================================================

val TealColor = Color(0xFF4396A5)
const val HOME_SCREEN_ROUTE = "home_screen" // صفحه شروع (صفحه لوگو و دکمه شروع)
const val LOGIN_SCREEN_ROUTE = "login_screen"
const val OTP_SCREEN_ROUTE = "otp_screen"
const val ROLE_SCREEN_ROUTE = "role_screen" // 🆕 مسیر جدید برای انتخاب نقش
const val APP_MAIN_ROUTE = "app_main_route" // 🆕 مسیر صفحه اصلی نهایی برنامه

// =================================================================
// کلاس اصلی فعالیت (Activity)
// =================================================================

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val navController = rememberNavController()

            GuidoraTheme {
                NavHost(
                    navController = navController,
                    startDestination = HOME_SCREEN_ROUTE
                ) {

                    // 1. مسیر صفحه شروع (GuidoraScreen)
                    composable(HOME_SCREEN_ROUTE) {
                        GuidoraScreen(
                            onConsultationClick = {
                                Log.d("Navigation", "Button Clicked! Navigating to Login.")
                                navController.navigate(LOGIN_SCREEN_ROUTE)
                            }
                        )
                    }

                    // 2. مسیر صفحه ورود (LoginScreen)
                    composable(LOGIN_SCREEN_ROUTE) {
                        LoginScreen(
                            onNavigateToOtp = {
                                Log.d("Navigation", "Received Code Button Clicked! Navigating to OTP.")
                                // انتقال به OTP و حذف Login از Back Stack
                                navController.navigate(OTP_SCREEN_ROUTE) {
                                    popUpTo(LOGIN_SCREEN_ROUTE) { inclusive = true }
                                }
                            }
                        )
                    }

                    // 3. مسیر صفحه تأیید کد (OTPScreen) - شامل ناوبری جدید به Role
                    composable(OTP_SCREEN_ROUTE) {
                        OTPScreen(
                            // بازگشت به صفحه قبل (لاگین)
                            onBackPressed = { navController.popBackStack() },

                            // 🚀 ناوبری جدید: در صورت موفقیت، به صفحه Role بروید
                            onVerificationSuccess = {
                                Log.d("Navigation", "OTP Success! Navigating to Role Screen.")
                                navController.navigate(ROLE_SCREEN_ROUTE) {
                                    // حذف OTP از Back Stack
                                    popUpTo(OTP_SCREEN_ROUTE) { inclusive = true }
                                }
                            }
                        )
                    }

                    // 4. مسیر صفحه انتخاب نقش (RoleScreen) - جدید
                    composable(ROLE_SCREEN_ROUTE) {
                        RoleScreen(
                            // ناوبری جدید: در صورت تکمیل نقش، به صفحه اصلی نهایی برنامه بروید
                            onLoginSuccess = {
                                Log.d("Navigation", "Role Selection Complete. Navigating to Main App.")
                                navController.navigate(APP_MAIN_ROUTE) {
                                    // پاک کردن تمام صفحات احراز هویت (Login, OTP, Role)
                                    popUpTo(HOME_SCREEN_ROUTE) { inclusive = true }
                                }
                            }
                        )
                    }

                    // 5. مسیر صفحه اصلی نهایی (APP_MAIN_ROUTE) - جدید
                    composable(APP_MAIN_ROUTE) {
                        // کامپوزبل موقت: این بخش را با صفحه اصلی اپلیکیشن خود جایگزین کنید
                        Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
                            Text(
                                "صفحه اصلی برنامه GUIDORA",
                                modifier = Modifier
                                    .fillMaxSize()
                                    .wrapContentSize(Alignment.Center),
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold,
                                color = TealColor
                            )
                        }
                    }
                }
            }
        }
    }
}

// =================================================================
// Composable ها (اجزای سازنده UI) - بدون تغییر
// =================================================================

@Composable
fun GuidoraScreen(
    onConsultationClick: () -> Unit
) {
    Surface(
        color = Color.White,
        modifier = Modifier.fillMaxSize()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {

            Spacer(modifier = Modifier.height(50.dp))

            // 1. لوگوی گرد آپلود شده
            Image(
                painter = painterResource(id = R.drawable.uploaded_logo),
                contentDescription = "لوگوی اصلی برنامه GUIDORA",
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .size(430.dp)
                    .clip(CircleShape)
                    .clickable { }
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 2. آیکون آدمک (بالای خطوط)
            Image(
                painter = painterResource(id = R.drawable.ic_person),
                contentDescription = "آیکون آدمک",
                modifier = Modifier.size(70.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            // 3. متن میانی با خطوط کناری
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                // خط جداکننده سمت راست
                Divider(
                    color = TealColor,
                    thickness = 1.dp,
                    modifier = Modifier.weight(1f).padding(end = 8.dp)
                )

                // متن میانی
                Text(
                    text = "تا خرد، فقط یک گفتگو لازمه",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = TealColor
                )

                // خط جداکننده سمت چپ
                Divider(
                    color = TealColor,
                    thickness = 1.dp,
                    modifier = Modifier.weight(1f).padding(start = 8.dp)
                )
            }

            Spacer(modifier = Modifier.height(60.dp))

            // 4. دکمه "شروع مشاوره"
            Button(
                onClick = onConsultationClick,
                colors = ButtonDefaults.buttonColors(containerColor = TealColor),
                shape = MaterialTheme.shapes.medium,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                // آیکون هدفون
                Image(
                    painter = painterResource(id = R.drawable.ic_headset),
                    contentDescription = "آیکون هدفون",
                    modifier = Modifier.size(24.dp)
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "شروع مشاوره",
                    fontSize = 20.sp,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}