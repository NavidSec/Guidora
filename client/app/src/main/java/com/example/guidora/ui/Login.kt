// LoginScreen.kt

package com.example.guidora.ui

import com.example.guidora.R
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.layout.ContentScale
import android.util.Log // ⬅️ ایمپورت اضافه شده

// =================================================================
// تعاریف رنگ‌ها
// =================================================================

val SendAgainColor = Color(0xFF4396A5)
val PrimaryTealColor = Color(0xFF4396A5)

// =================================================================
// صفحه اصلی LoginScreen
// =================================================================

@Composable
fun LoginScreen(onNavigateToOtp: () -> Unit) { // ⬅️ پارامتر مسیریابی
    var phoneNumber by remember { mutableStateOf(TextFieldValue("")) }

    val humanIconSize = 60.dp
    val phoneIconSize = 20.dp
    val resendIconSize = 20.dp

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(horizontal = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(80.dp))

        // 1. بخش لوگوی گرد
        LogoSection(logoDrawableId = R.drawable.uploaded_logo)

        Spacer(modifier = Modifier.height(20.dp))

        // 2. آیکون آدمک و خط افقی
        HumanIconDivider(
            humanIconDrawableId = R.drawable.ic_person,
            iconSize = humanIconSize
        )

        Spacer(modifier = Modifier.height(48.dp))

        // 3. فیلد ورودی شماره موبایل
        PhoneNumberInputField(
            value = phoneNumber,
            onValueChange = { phoneNumber = it },
            phoneIconDrawableId = R.drawable.your_phone_icon,
            iconSize = phoneIconSize
        )

        Spacer(modifier = Modifier.height(24.dp))

        // 4. دکمه دریافت کد
        ReceiveCodeButton(
            onClick = onNavigateToOtp, // ⬅️ پاس دادن منطق مسیریابی
            primaryColor = PrimaryTealColor
        )

        Spacer(modifier = Modifier.height(16.dp))

        // 5. متن ارسال مجدد
        ResendCodeText(
            onClick = { /* منطق ارسال مجدد کد */ },
            iconDrawableId = R.drawable.your_resend_icon,
            iconSize = resendIconSize
        )
    }
}

// =================================================================
// Composable های فرعی
// =================================================================

@Composable
fun LogoSection(logoDrawableId: Int) {
    Box(
        modifier = Modifier
            .size(400.dp)
            .clip(CircleShape)
            .background(Color.White),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = logoDrawableId),
            contentDescription = "Guidora Logo",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )
    }
}

@Composable
fun HumanIconDivider(humanIconDrawableId: Int, iconSize: Dp) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Divider(
            color = Color.LightGray.copy(alpha = 0.6f),
            modifier = Modifier.weight(1f).height(1.dp)
        )

        Spacer(modifier = Modifier.width(16.dp))

        Image(
            painter = painterResource(id = humanIconDrawableId),
            contentDescription = "Human Icon",
            modifier = Modifier.size(iconSize)
        )

        Spacer(modifier = Modifier.width(16.dp))

        Divider(
            color = Color.LightGray.copy(alpha = 0.6f),
            modifier = Modifier.weight(1f).height(1.dp)
        )
    }
}

@Composable
fun PhoneNumberInputField(value: TextFieldValue, onValueChange: (TextFieldValue) -> Unit, phoneIconDrawableId: Int, iconSize: Dp) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp)
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0xFFE8E8E8)),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // 1. فیلد ورودی شماره
        BasicTextField(
            value = value,
            onValueChange = onValueChange,
            textStyle = TextStyle(
                fontSize = 16.sp,
                color = Color.Black,
                textAlign = TextAlign.Right
            ),
            modifier = Modifier
                .weight(1f)
                .padding(start = 16.dp, end = 8.dp),

            // تنظیمات متن جایگزین (Placeholder)
            decorationBox = { innerTextField ->
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.CenterEnd
                ) {
                    if (value.text.isEmpty()) {
                        Text(
                            text = "شماره موبایل خود را وارد کنید",
                            color = Color.Gray,
                            fontSize = 16.sp,
                            textAlign = TextAlign.Right,
                        )
                    }
                    innerTextField()
                }
            }
        )

        // 2. آیکون موبایل
        Image(
            painter = painterResource(id = phoneIconDrawableId),
            contentDescription = "Phone Icon",
            modifier = Modifier
                .padding(start = 8.dp, end = 16.dp)
                .size(iconSize)
        )
    }
}

@Composable
fun ReceiveCodeButton(onClick: () -> Unit, primaryColor: Color) {
    Button(
        onClick = {
            Log.d("NAV_TEST", "Button clicked and trying to navigate!") // ⬅️ Log برای تست
            onClick()
        },
        colors = ButtonDefaults.buttonColors(backgroundColor = primaryColor),
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp),
        shape = RoundedCornerShape(8.dp),
        elevation = ButtonDefaults.elevation(0.dp)
    ) {
        Text(
            text = "دریافت کد",
            color = Color.White,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun ResendCodeText(onClick: () -> Unit, iconDrawableId: Int, iconSize: Dp) {
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {

        TextButton(onClick = onClick) {
            Text(
                text = "ارسال مجدد",
                color = SendAgainColor,
                fontSize = 18.sp
            )
        }

//        Spacer(modifier = Modifier.width(1.dp))
        Image(
            painter = painterResource(id = iconDrawableId),
            contentDescription = "Resend Icon",
            modifier = Modifier.size(iconSize)
        )

    }
}