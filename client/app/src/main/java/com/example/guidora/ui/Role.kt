package com.example.guidora.ui

import androidx.compose.foundation.text.BasicTextField
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.*
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.guidora.R

// تعریف رنگ‌ها
val DividerColor = Color(0xFF4396A5)
val InputFieldColor = Color(0xFFE0E0E0)
val ButtonColor = Color(0xFF4396A5)


@Composable
fun RoleScreen(
    onLoginSuccess: () -> Unit
) {
    var isDropdownExpanded by remember { mutableStateOf(false) }
    var selectedRole by remember { mutableStateOf("نوع کاربر") }
    var nameText by remember { mutableStateOf("") }
    var familyText by remember { mutableStateOf("") }

    val roles = listOf("کاربر ساده", "مشاور حقوقی", "مشاور تحصیلی")

    val rotationAngle by animateFloatAsState(
        targetValue = if (isDropdownExpanded) 180f else 0f,
        animationSpec = tween(durationMillis = 300), label = ""
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        // 1. **بخش لوگو Guidora**
        Box(
            modifier = Modifier
                .size(350.dp)
                .clip(RoundedCornerShape(75.dp)),
            contentAlignment = Alignment.Center
        ) {
            Image(
                painter = painterResource(id = R.drawable.uploaded_logo),
                contentDescription = "لوگوی Guidora",
                modifier = Modifier
                    .size(350.dp),
                contentScale = ContentScale.Fit
            )
        }

        Spacer(modifier = Modifier.height(10.dp))

        // 2. **خطوط و آیکون آدمک**
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Divider(
                color = DividerColor,
                modifier = Modifier
                    .weight(1f)
                    .height(1.dp)
            )

            Image(
                painter = painterResource(id = R.drawable.ic_person),
                contentDescription = "آیکون کاربر",
                modifier = Modifier
                    .size(70.dp)
                    .padding(horizontal = 8.dp),
                contentScale = ContentScale.Fit
            )

            Divider(
                color = DividerColor,
                modifier = Modifier
                    .weight(1f)
                    .height(1.dp)
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        // 3. **فیلدهای ورودی (نام و نام خانوادگی)**
        InputField(
            value = nameText,
            // ⬅️ منطق فیلتر کردن اعداد به اینجا اعمال می‌شود
            onValueChange = { newValue ->
                if (newValue.all { it.isLetter() || it.isWhitespace() }) {
                    nameText = newValue
                }
            },
            iconId = R.drawable.personfill,
            placeholder = "نام"
        )

        Spacer(modifier = Modifier.height(16.dp))

        InputField(
            value = familyText,
            // ⬅️ منطق فیلتر کردن اعداد به اینجا اعمال می‌شود
            onValueChange = { newValue ->
                if (newValue.all { it.isLetter() || it.isWhitespace() }) {
                    familyText = newValue
                }
            },
            iconId = R.drawable.personfill,
            placeholder = "نام خانوادگی",
        )

        Spacer(modifier = Modifier.height(16.dp))

        // 4. **منوی کشویی نوع کاربر**
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            // دکمه نمایش منو
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(InputFieldColor)
                    .clickable { isDropdownExpanded = !isDropdownExpanded }
                    .padding(horizontal = 16.dp, vertical = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Start
            ) {
                // آیکون فلش (سمت چپ)
                Image(
                    painter = painterResource(id = R.drawable.downarrow),
                    contentDescription = "فلش باز شدن",
                    modifier = Modifier
                        .size(24.dp)
                        .rotate(rotationAngle)
                        .align(Alignment.CenterVertically)
                )

                // متن نوع کاربر (وسط، راست‌چین) - اعمال تغییر رنگ
                Text(
                    text = selectedRole,
                    color = if (selectedRole == "نوع کاربر") Color.DarkGray else Color.Black,
                    fontSize = 16.sp,
                    modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp),
                    textAlign = TextAlign.Right
                )

                // آیکون آدمک‌های گروهی (سمت راست - آیکون اصلی فیلد)
                Image(
                    painter = painterResource(id = R.drawable.person2fill),
                    contentDescription = "آیکون گروه",
                    modifier = Modifier.size(24.dp)
                )
            }

            // نمایش منوی کشویی
            AnimatedVisibility(visible = isDropdownExpanded) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 4.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(InputFieldColor)
                        .padding(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    roles.forEach { role ->
                        Text(
                            text = role,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    selectedRole = role
                                    isDropdownExpanded = false
                                }
                                .padding(vertical = 10.dp, horizontal = 16.dp),
                            fontSize = 16.sp,
                            textAlign = TextAlign.Right
                        )
                        if (role != roles.last()) {
                            Divider(color = Color.LightGray, thickness = 1.dp)
                        }
                    }
                }
            }
        }


        Spacer(modifier = Modifier.height(32.dp))

        // 5. **دکمه ورود (Login Button)**
        Button(
            onClick = onLoginSuccess,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
                .clip(RoundedCornerShape(12.dp)),

            colors = ButtonDefaults.buttonColors(
                backgroundColor = ButtonColor,
                contentColor = Color.White
            ),
            elevation = ButtonDefaults.elevation(defaultElevation = 0.dp)
        ) {
            Text(
                text = "ورود",
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

// کامپوزبل کمکی InputField
// (توجه: پارامتر onValueChange در اینجا همچنان همان تابع کلی است،
// اما فیلترینگ واقعی در داخل RoleScreen (جایی که state مدیریت می‌شود) اعمال شده است.)
@Composable
fun InputField(value: String, onValueChange: (String) -> Unit, placeholder: String, iconId: Int) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(InputFieldColor)
            .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Start
    ) {

        // ✅ ۱. Spacer جبرانی برای هم‌ترازی با آیکون فلش در منوی کشویی
        Spacer(modifier = Modifier.size(24.dp))

        // ۲. فیلد متنی واقعی
        BasicTextField(
            value = value,
            onValueChange = onValueChange, // ⬅️ onValueChange فیلتر شده از RoleScreen را دریافت می‌کند
            textStyle = TextStyle(
                fontSize = 16.sp,
                color = Color.Black,
                textAlign = TextAlign.Right
            ),
            modifier = Modifier
                .weight(1f)
                .padding(horizontal = 8.dp),
            singleLine = true,
            decorationBox = { innerTextField ->
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.CenterEnd
                ) {
                    if (value.isEmpty()) {
                        // نمایش Placeholder (راست‌چین)
                        Text(
                            text = placeholder,
                            color = Color.DarkGray,
                            fontSize = 16.sp,
                            textAlign = TextAlign.Right,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                    innerTextField()
                }
            }
        )

        // ۳. آیکون اصلی فیلد (سمت راست)
        Image(
            painter = painterResource(id = iconId),
            contentDescription = "آیکون فیلد",
            modifier = Modifier.size(24.dp)
        )
    }
}